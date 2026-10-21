import unittest

from redfox_data_mcp.dispatch import prepare
from redfox_data_mcp.search import describe, find


class SchemaTests(unittest.TestCase):
    def test_instructions_name_platforms_and_rank_category(self):
        from redfox_data_mcp.schema import instructions, param_specs

        text = instructions()
        self.assertIn("douyin（抖音）", text)
        self.assertIn("douyin.get.daily.hot.rank", text)
        self.assertIn("体育", text)
        described = {item["name"]: item["description"] for item in param_specs()}
        self.assertTrue(described["type"].startswith("榜单或推荐的分类"))
        self.assertIn("体育", described["type"])
        self.assertIn("keyword", described)
        self.assertNotIn("ai_gen", text)
        self.assertNotIn("tools（", text)
        self.assertNotIn("上传", text)


class HiddenPlatformTests(unittest.TestCase):
    def test_download_and_image_gen_stay_out_of_the_catalog(self):
        from redfox_data_mcp.search import load_catalog

        ids = [item["id"] for item in load_catalog()]
        self.assertEqual(len(ids), 102)
        self.assertFalse(any(item.startswith(("tools.", "ai_gen.")) for item in ids))
        hidden = describe(["tools.download", "ai_gen.gpt.image.generate", "douyin.get.daily.hot.rank"])
        self.assertEqual(hidden["missing"], ["tools.download", "ai_gen.gpt.image.generate"])
        self.assertEqual([item["id"] for item in hidden["capabilities"]], ["douyin.get.daily.hot.rank"])
        looked = find("下载图片")
        self.assertFalse(any(item["id"].startswith(("tools.", "ai_gen.")) for item in looked["matches"] + looked["nearest"]))
        self.assertIsInstance(prepare("tools.upload.image", {"file": "a.png", "format": "png"}), dict)


class FindTests(unittest.TestCase):
    def test_douyin_hot_is_lexical(self):
        result = find("抖音热门作品")
        self.assertNotIn("error", result)
        ids = [item["id"] for item in result["matches"]]
        self.assertTrue(ids)
        self.assertLessEqual(len(ids), 10)
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

    def test_kimi_search(self):
        result = find("kimi 联网搜索")
        ids = [item["id"] for item in result["matches"]]
        self.assertEqual(ids[0], "ai_search.kimi")

    def test_broad_query_caps_at_ten(self):
        result = find("搜索")
        self.assertLessEqual(len(result["matches"]), 10)

    def test_describe_and_prepare_reject_before_call(self):
        described = describe(["douyin.search.articles"])
        self.assertEqual(described["missing"], [])
        self.assertTrue(described["capabilities"][0]["params"])
        rejected = prepare("douyin.search.articles", {})
        self.assertIsInstance(rejected, dict)
        self.assertEqual(rejected["error"], "invalid_argument")
        missing_cap = prepare("douyin.private.messages", {"keyword": "x"})
        self.assertEqual(missing_cap["error"], "invalid_argument")


if __name__ == "__main__":
    unittest.main()
