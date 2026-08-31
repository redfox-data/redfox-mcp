"""RedFox X(Twitter) 数据 MCP Server

将 RedFoxHub（红狐数据平台）的 X(Twitter) 数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_twitter_mcp import __version__

mcp = create_server("redfox-twitter", __version__)


@mcp.tool()
def twitter_search_tweets(keyword: str, search_type: Optional[str] = None,
                          cursor: Optional[str] = None) -> Dict[str, Any]:
    """X(Twitter) 关键词搜索推文。keyword 必填；
    search_type：Top/Latest/Media/People/Lists；cursor 用于翻页。"""
    return call(lambda: get_client().twitter.search_tweets,
                keyword=keyword, search_type=search_type, cursor=cursor)


@mcp.tool()
def twitter_get_tweet(tweet_id: str) -> Dict[str, Any]:
    """获取 X(Twitter) 单条推文详情。tweet_id 为推文 ID（必填）。"""
    return call(lambda: get_client().twitter.get_tweet, tweet_id=tweet_id)


@mcp.tool()
def twitter_get_user(screen_name: Optional[str] = None,
                     rest_id: Optional[str] = None) -> Dict[str, Any]:
    """获取 X(Twitter) 用户信息。screen_name 与 rest_id 至少传一个。"""
    return call(lambda: get_client().twitter.get_user,
                screen_name=screen_name, rest_id=rest_id)


@mcp.tool()
def twitter_get_comments(tweet_id: str,
                         cursor: Optional[str] = None) -> Dict[str, Any]:
    """获取 X(Twitter) 推文评论/回复。tweet_id 必填；cursor 用于翻页。"""
    return call(lambda: get_client().twitter.get_comments,
                tweet_id=tweet_id, cursor=cursor)


def main() -> None:
    serve(mcp, prog="redfox-twitter-mcp", description="RedFox X(Twitter) MCP server")


if __name__ == "__main__":
    main()
