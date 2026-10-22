import unittest

from redfox_data_mcp.dispatch import prepare
from redfox_data_mcp.search import describe, find


class SchemaTests(unittest.TestCase):
    def test_instructions_name_platforms_and_rank_category(self):
        from redfox_data_mcp.schema import capability_ids, instructions, param_specs

        text = instructions()
        self.assertTrue(text.startswith("红狐数据(RedFox)提供抖音、快手、微信公众号、微信视频号、B站、头条、TikTok、Instagram、X（推特）、YouTube、懂车帝、汽车之家、易车等平台的公开数据能力。"))
        self.assertIn("douyin.get.daily.hot.rank", text)
        self.assertIn("抖音：", text)
        self.assertIn("体育", text)
        self.assertNotIn("小红书", text)
        self.assertNotIn("xiaohongshu", text)
        described = {item["name"]: item["description"] for item in param_specs()}
        self.assertTrue(described["type"].startswith("榜单或推荐的分类"))
        self.assertIn("体育", described["type"])
        self.assertIn("keyword", described)
        self.assertNotIn("ai_gen", text)
        self.assertNotIn("ai_search", text)
        self.assertNotIn("AI 搜索", text)
        self.assertNotIn("tools（", text)
        self.assertNotIn("上传", text)
        self.assertIn("https://redfox.hk?source=doubaobangong", text)
        self.assertIn("红狐数据工具暂无当前数据", text)
        self.assertIn("抖音：", text)
        self.assertIn("快手：", text)
        self.assertIn("TikTok：", text)
        from redfox_data_mcp.schema import find_param_descriptions

        fields = find_param_descriptions()
        self.assertIn("抖音体育榜单", fields["query"])
        self.assertIn("douyin（抖音）", fields["platform"])
        self.assertNotIn("下载与上传", fields["platform"])
        self.assertNotIn("AI 生成", fields["platform"])
        self.assertNotIn("小红书", fields["platform"])
        self.assertIn("social", fields["category"])
        self.assertIn("auto", fields["category"])
        self.assertNotIn("tools", fields["category"])
        for name, desc in described.items():
            self.assertFalse(desc.startswith("参数 "), name)
            self.assertNotIn("上传", desc)
            self.assertNotIn("文生图", desc)
            self.assertNotIn("小红书", desc)


class HiddenPlatformTests(unittest.TestCase):
    def test_download_and_image_gen_stay_out_of_the_catalog(self):
        from redfox_data_mcp.search import load_catalog

        ids = [item["id"] for item in load_catalog()]
        self.assertEqual(len(ids), 83)
        self.assertFalse(any(item.startswith(("tools.", "ai_gen.", "ai_search.", "xiaohongshu.")) for item in ids))
        hidden = describe([
            "tools.download",
            "ai_gen.gpt.image.generate",
            "ai_search.kimi",
            "xiaohongshu.search.articles",
            "douyin.get.daily.hot.rank",
        ])
        self.assertEqual(
            hidden["missing"],
            ["tools.download", "ai_gen.gpt.image.generate", "ai_search.kimi", "xiaohongshu.search.articles"],
        )
        self.assertEqual([item["id"] for item in hidden["capabilities"]], ["douyin.get.daily.hot.rank"])
        looked = find("下载图片")
        self.assertFalse(any(item["id"].startswith(("tools.", "ai_gen.")) for item in looked["matches"] + looked["nearest"]))
        self.assertIsInstance(prepare("tools.upload.image", {"file": "a.png", "format": "png"}), dict)
        xhs = find("小红书笔记")
        self.assertFalse(any(item["id"].startswith("xiaohongshu.") for item in xhs["matches"] + xhs["nearest"]))
        self.assertIsInstance(prepare("xiaohongshu.search.articles", {"keyword": "露营"}), dict)


class FindTests(unittest.TestCase):
    def test_douyin_hot_is_lexical(self):
        result = find("抖音热门作品")
        self.assertNotIn("error", result)
        ids = [item["id"] for item in result["matches"]]
        self.assertTrue(ids)
        self.assertLessEqual(len(ids), 6)
        self.assertTrue(all(item.startswith("douyin.") for item in ids))
        self.assertIn("douyin", result["platforms"])

    def test_platform_only_lists_nearest_without_matches(self):
        result = find(platform="抖音")
        self.assertEqual(result["matches"], [])
        self.assertGreaterEqual(len(result["nearest"]), 10)
        self.assertTrue(all(item["id"].startswith("douyin.") for item in result["nearest"]))

    def test_unknown_need_does_not_substitute(self):
        result = find("抖音天气预报")
        self.assertEqual(result["matches"], [])
        self.assertTrue(result["unknown"])
        self.assertTrue(result["nearest"])

    def test_kimi_search_is_closed(self):
        result = find("kimi 联网搜索")
        ids = [item["id"] for item in result["matches"]]
        self.assertNotIn("ai_search.kimi", ids)

    def test_broad_query_caps_at_six(self):
        result = find("搜索")
        self.assertLessEqual(len(result["matches"]), 6)

    def test_describe_and_prepare_reject_before_call(self):
        described = describe(["douyin.search.articles"])
        self.assertEqual(described["missing"], [])
        self.assertTrue(described["capabilities"][0]["params"])
        rejected = prepare("douyin.search.articles", {})
        self.assertIsInstance(rejected, dict)
        self.assertEqual(rejected["error"], "invalid_argument")
        missing_cap = prepare("douyin.private.messages", {"keyword": "x"})
        self.assertEqual(missing_cap["error"], "invalid_argument")

    def test_prepare_uses_doubaobangong_source(self):
        from redfox_data_mcp.dispatch import CALL_SOURCE

        item, payload, _timeout = prepare("douyin.get.daily.hot.rank", {"type": "体育"})
        self.assertEqual(item["id"], "douyin.get.daily.hot.rank")
        self.assertEqual(payload["source"], CALL_SOURCE)
        self.assertEqual(payload["source"], "doubaobangong")
        self.assertEqual(payload["type"], "体育")


class ConsentUrlTests(unittest.TestCase):
    def test_consent_redirect_adds_source_and_txn(self):
        from redfox_data_mcp.oauth import CONSENT_SOURCE, _with_txn
        from urllib.parse import parse_qs, urlsplit

        url = _with_txn("https://redfox.hk/oauth/consent", "txn-abc")
        query = parse_qs(urlsplit(url).query)
        self.assertEqual(query["source"], [CONSENT_SOURCE])
        self.assertEqual(query["txn_id"], ["txn-abc"])
        kept = _with_txn("https://redfox.hk/oauth/consent?source=keep-me", "txn-2")
        kept_query = parse_qs(urlsplit(kept).query)
        self.assertEqual(kept_query["source"], ["keep-me"])
        self.assertEqual(kept_query["txn_id"], ["txn-2"])


if __name__ == "__main__":
    unittest.main()
