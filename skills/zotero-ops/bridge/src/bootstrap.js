// ZCode Bridge v0.1.0 — 本地 HTTP 桥，让 AI 代理（ZCode 等）可以完整操作本机 Zotero 文库。
// 端点：GET/POST /zcode/ping ；POST /zcode/rpc  {"op": "...", ...}
// 能力：items 列表/创建/更新/删除、条目分类归属、collection 创建/更新、
//       本地文件挂为附件（导入或链接）、selftest、zotero.eval（需 pref extensions.zcode-bridge.allowEval=true）
// v3：纯 XPCOM 日志（不依赖 Zotero API）+ 全阶段标记 + 端点注册重试。

// 日志写到系统临时目录（跨机器/跨系统可写）。想换位置：把 "TmpD" 换成 "ProfD"（profile 目录），或直接改字符串路径。
var LOG_PATH = (function () {
  try {
    var ds = Components.classes["@mozilla.org/file/directory_service;1"]
      .getService(Components.interfaces.nsIProperties);
    var f = ds.get("TmpD", Components.interfaces.nsIFile);
    f.append("zcode-bridge.log");
    return f.path;
  } catch (e) { return "zcode-bridge.log"; }
})();

function rawLog(msg) {
  try {
    var f = Components.classes["@mozilla.org/file/local;1"].createInstance(Components.interfaces.nsIFile);
    f.initWithPath(LOG_PATH);
    var s = Components.classes["@mozilla.org/network/file-output-stream;1"].createInstance(Components.interfaces.nsIFileOutputStream);
    s.init(f, 0x02 | 0x08 | 0x10, 0o666, 0); // WRONLY | CREATE | APPEND
    var str = new Date().toISOString() + "  " + msg + "\n";
    s.write(str, str.length);
    s.close();
  } catch (e) {}
}

function delay(ms) {
  return new Promise(function (resolve) {
    var timer = Components.classes["@mozilla.org/timer;1"].createInstance(Components.interfaces.nsITimer);
    timer.initWithCallback(resolve, ms, Components.interfaces.nsITimer.TYPE_ONE_SHOT);
  });
}

rawLog("== bootstrap.js scope loaded (top-level) ==");

function install(data, reason) {
  rawLog("install() called, reason=" + reason);
}
function uninstall(data, reason) {
  rawLog("uninstall() called, reason=" + reason);
}

async function startup({ id, version, rootURI }, reason) {
  rawLog("startup() called, id=" + id + " version=" + version + " reason=" + reason);
  // Zotero 7+ 插件沙箱中 Zotero 是全局对象（jasminum/zotmoov 同款用法）；等待应用初始化完成。
  try {
    await Zotero.initializationPromise;
    rawLog("Zotero ready, version=" + Zotero.version);
  } catch (e) {
    rawLog("Zotero initialization failed: " + (e && e.message ? e.message : e));
    try {
      Zotero = Components.classes["@zotero.org/Zotero;1"]
        .getService(Components.interfaces.nsISupports).wrappedJSObject;
      rawLog("fallback acquisition OK, version=" + Zotero.version);
    } catch (e2) {
      rawLog("fallback acquisition also failed: " + (e2 && e2.message ? e2.message : e2));
      return;
    }
  }

  function ok(result) {
    return [200, "application/json", JSON.stringify({ ok: true, result: result === undefined ? null : result })];
  }
  function fail(status, error) {
    return [status, "application/json", JSON.stringify({ ok: false, error: String(error && error.message ? error.message : error) })];
  }
  async function getCollectionByKey(key) {
    var c = Zotero.Collections.getByLibraryAndKeyAsync
      ? await Zotero.Collections.getByLibraryAndKeyAsync(Zotero.Libraries.userLibraryID, key)
      : await Zotero.Collections.getByLibraryAndKey(Zotero.Libraries.userLibraryID, key);
    return c || null;
  }
  async function getItemByKey(key) {
    var it = Zotero.Items.getByLibraryAndKeyAsync
      ? await Zotero.Items.getByLibraryAndKeyAsync(Zotero.Libraries.userLibraryID, key)
      : await Zotero.Items.getByLibraryAndKey(Zotero.Libraries.userLibraryID, key);
    return it || null;
  }
  function collectionKey(id) {
    try { var c = Zotero.Collections.get(id); return c ? c.key : null; } catch (e) { return null; }
  }

  var ops = {};

  ops["ping"] = async function () {
    return { plugin: "zcode-bridge", version: "0.1.0", zotero: Zotero.version, libraryID: Zotero.Libraries.userLibraryID };
  };

  ops["selftest"] = async function () {
    var item = new Zotero.Item("document");
    item.setField("title", "__ZCode Bridge selftest__ " + new Date().toISOString());
    await item.saveTx();
    var key = item.key;
    await item.eraseTx();
    return { created: key, erased: true };
  };

  ops["collections.list"] = async function () {
    var rows = await Zotero.DB.queryAsync(
      "SELECT collectionID, collectionName, parentCollectionID, key FROM collections WHERE libraryID=?",
      [Zotero.Libraries.userLibraryID]
    );
    return (rows || []).map(function (r) {
      return {
        id: r.collectionID,
        key: r.key,
        name: r.collectionName,
        parentCollectionID: r.parentCollectionID || null,
        parentKey: r.parentCollectionID ? collectionKey(r.parentCollectionID) : null
      };
    });
  };

  ops["items.list"] = async function () {
    var items = await Zotero.Items.getAll(Zotero.Libraries.userLibraryID, false, false);
    items = items || [];
    var id2key = {};
    var rows = await Zotero.DB.queryAsync("SELECT collectionID, key FROM collections", []);
    (rows || []).forEach(function (r) { id2key[r.collectionID] = r.key; });
    var out = [];
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      out.push({
        key: it.key,
        itemType: Zotero.ItemTypes.getName(it.itemTypeID),
        title: it.getField("title") || "",
        parentKey: it.parentKey || null,
        collections: (it.getCollections() || []).map(function (id) { return id2key[id] || null; }),
        tags: (it.getTags() || []).map(function (t) { return t.tag; }),
        deleted: !!it.deleted
      });
    }
    return out;
  };

  ops["item.create"] = async function (body) {
    var item = new Zotero.Item(body.itemType || "journalArticle");
    var errors = [];
    var fields = body.fields || {};
    for (var f in fields) {
      try { item.setField(f, fields[f]); } catch (e) { errors.push(f + ": " + e.message); }
    }
    if (body.creators) {
      try {
        item.setCreators(body.creators.map(function (c) {
          return { creatorType: c.creatorType || "author", firstName: c.firstName || "", lastName: c.lastName || "" };
        }));
      } catch (e) { errors.push("creators: " + e.message); }
    }
    if (body.tags) {
      try {
        item.setTags(body.tags.map(function (t) { return { tag: typeof t === "string" ? t : t.tag }; }));
      } catch (e) { errors.push("tags: " + e.message); }
    }
    await item.saveTx();
    if (body.collections && body.collections.length) {
      for (var i = 0; i < body.collections.length; i++) {
        var c = await getCollectionByKey(body.collections[i]);
        if (!c) { errors.push("collection not found: " + body.collections[i]); continue; }
        item.addToCollection(c.id);
      }
      await item.saveTx();
    }
    return { key: item.key, errors: errors };
  };

  ops["item.update"] = async function (body) {
    var item = await getItemByKey(body.key);
    if (!item) throw new Error("item not found: " + body.key);
    var errors = [];
    var fields = body.fields || {};
    for (var f in fields) {
      try { item.setField(f, fields[f]); } catch (e) { errors.push(f + ": " + e.message); }
    }
    if (body.tagsAdd) {
      for (var i = 0; i < body.tagsAdd.length; i++) {
        try { item.addTag(typeof body.tagsAdd[i] === "string" ? body.tagsAdd[i] : body.tagsAdd[i].tag, 0); }
        catch (e) { errors.push("tagAdd: " + e.message); }
      }
    }
    if (body.tagsRemove) {
      for (var j = 0; j < body.tagsRemove.length; j++) {
        try { item.removeTag(typeof body.tagsRemove[j] === "string" ? body.tagsRemove[j] : body.tagsRemove[j].tag); }
        catch (e) { errors.push("tagRemove: " + e.message); }
      }
    }
    if (body.creators) {
      try {
        item.setCreators(body.creators.map(function (c) {
          return { creatorType: c.creatorType || "author", firstName: c.firstName || "", lastName: c.lastName || "" };
        }));
      } catch (e) { errors.push("creators: " + e.message); }
    }
    await item.saveTx();
    return { key: item.key, errors: errors };
  };

  ops["item.delete"] = async function (body) {
    var item = await getItemByKey(body.key);
    if (!item) throw new Error("item not found: " + body.key);
    if (body.erase) { await item.eraseTx(); return { key: body.key, erased: true }; }
    item.deleted = true;
    await item.saveTx();
    return { key: body.key, trashed: true };
  };

  ops["item.setCollections"] = async function (body) {
    var item = await getItemByKey(body.key);
    if (!item) throw new Error("item not found: " + body.key);
    var ids = [];
    for (var i = 0; i < (body.collections || []).length; i++) {
      var c = await getCollectionByKey(body.collections[i]);
      if (!c) throw new Error("collection not found: " + body.collections[i]);
      ids.push(c.id);
    }
    var current = item.getCollections();
    var mode = body.mode || "replace";
    if (mode === "replace") {
      for (var j = 0; j < current.length; j++) if (ids.indexOf(current[j]) === -1) item.removeFromCollection(current[j]);
      for (var k = 0; k < ids.length; k++) if (current.indexOf(ids[k]) === -1) item.addToCollection(ids[k]);
    } else if (mode === "remove") {
      for (var m = 0; m < ids.length; m++) if (current.indexOf(ids[m]) !== -1) item.removeFromCollection(ids[m]);
    } else {
      for (var n = 0; n < ids.length; n++) if (current.indexOf(ids[n]) === -1) item.addToCollection(ids[n]);
    }
    await item.saveTx();
    return { key: item.key, collections: item.getCollections().map(collectionKey) };
  };

  ops["collection.create"] = async function (body) {
    var c = new Zotero.Collection();
    c.libraryID = Zotero.Libraries.userLibraryID;
    c.name = body.name;
    if (body.parentKey) {
      var p = await getCollectionByKey(body.parentKey);
      if (!p) throw new Error("parent not found: " + body.parentKey);
      c.parentID = p.id;
    }
    await c.saveTx();
    return { key: c.key, name: c.name };
  };

  ops["collection.update"] = async function (body) {
    var c = await getCollectionByKey(body.key);
    if (!c) throw new Error("collection not found: " + body.key);
    if (typeof body.name === "string" && body.name) c.name = body.name;
    if ("parentKey" in body) {
      if (body.parentKey) {
        var p = await getCollectionByKey(body.parentKey);
        if (!p) throw new Error("parent not found: " + body.parentKey);
        c.parentID = p.id;
      } else {
        c.parentID = null;
      }
    }
    await c.saveTx();
    return { key: c.key, name: c.name, parentKey: collectionKey(c.parentID) };
  };

  ops["attachment.importFile"] = async function (body) {
    var file = Zotero.File.pathToFile(body.path);
    if (!file.exists()) throw new Error("file not found: " + body.path);
    var parentItemID = null;
    if (body.parentKey) {
      var parent = await getItemByKey(body.parentKey);
      if (!parent) throw new Error("parent item not found: " + body.parentKey);
      parentItemID = parent.id;
    }
    var att;
    if (body.linkMode === "linked_file") {
      att = await Zotero.Attachments.linkFromFile({ file: file, parentItemID: parentItemID });
    } else {
      att = await Zotero.Attachments.importFromFile({ file: file, parentItemID: parentItemID });
    }
    if (body.title && att) {
      try { att.setField("title", body.title); await att.saveTx(); } catch (e) {}
    }
    return { key: att.key, parentKey: body.parentKey || null, path: body.path, linkMode: body.linkMode || "imported_file" };
  };

  ops["zotero.eval"] = async function (body) {
    if (!Zotero.Prefs.get("extensions.zcode-bridge.allowEval", true)) {
      throw new Error("eval disabled: set pref extensions.zcode-bridge.allowEval=true and restart Zotero");
    }
    var result = await eval("(async () => {" + body.code + "})()");
    try { return { value: JSON.parse(JSON.stringify(result === undefined ? null : result)) }; }
    catch (e) { return { stringified: String(result) }; }
  };

  // ---------------- 端点注册（带重试，防 Server 未就绪） ----------------
  async function registerEndpoints(attempt) {
    if (!Zotero.Server || !Zotero.Server.Endpoints) {
      if (attempt < 120) {
        await delay(500);
        return registerEndpoints(attempt + 1);
      }
      throw new Error("Zotero.Server.Endpoints 不可用（重试 " + attempt + " 次后放弃）");
    }
    rawLog("registerEndpoints: Server.Endpoints 可用 (attempt " + attempt + ")");

    Zotero.Server.Endpoints["/zcode/ping"] = function () {};
    Zotero.Server.Endpoints["/zcode/ping"].prototype = {
      supportedMethods: ["GET", "POST"],
      init: async function (options) {
        rawLog("ping hit, method=" + (options && options.method) + " dataLen=" + (options && options.data ? String(options.data).length : 0));
        return ok({ plugin: "zcode-bridge", version: "0.1.0", zotero: Zotero.version, endpoints: ["/zcode/ping", "/zcode/rpc"] });
      }
    };

    Zotero.Server.Endpoints["/zcode/rpc"] = function () {};
    Zotero.Server.Endpoints["/zcode/rpc"].prototype = {
      supportedMethods: ["POST"],
      init: async function (options) {
        var raw = options && options.data;
        var body = {};
        rawLog("rpc hit, dataType=" + typeof raw + " len=" + (raw ? String(raw).length : 0) + " head=" + String(raw || "").slice(0, 100).replace(/\s+/g, " "));
        if (raw && typeof raw === "string") {
          try { body = JSON.parse(raw); }
          catch (e) { return fail(400, "invalid JSON body: " + String(raw).slice(0, 80)); }
        } else if (raw && typeof raw === "object") {
          body = raw;
        }
        var op = body.op;
        if (!op) return fail(400, "missing op");
        if (!ops[op]) return fail(400, "unknown op: " + op);
        try {
          var result = await ops[op](body);
          return ok(result);
        } catch (e) {
          rawLog("op " + op + " failed: " + (e && e.message ? e.message : e));
          return fail(500, e);
        }
      }
    };
    rawLog("endpoints registered OK (attempt " + attempt + ")");
  }

  try {
    await registerEndpoints(0);
  } catch (e) {
    rawLog("registerEndpoints FATAL: " + (e && e.message ? e.message : e));
  }
}

function shutdown() {
  rawLog("shutdown() called");
  try {
    delete Zotero.Server.Endpoints["/zcode/ping"];
    delete Zotero.Server.Endpoints["/zcode/rpc"];
  } catch (e) {}
}
