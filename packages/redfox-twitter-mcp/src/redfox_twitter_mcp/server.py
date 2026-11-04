"""RedFox X(Twitter) 数据 MCP Server

将 RedFoxHub（红狐数据平台）的 X(Twitter) 数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict, Optional
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_twitter_mcp import __version__

mcp = create_server("redfox-twitter", __version__)


@mcp.tool()
def twitter_search_tweets(keyword: Annotated[str, Field(description="搜索关键字，[必填]，示例: 南浔")], search_type: Annotated[Optional[str], Field(description="搜索类型，默认Top，可选：Top, Latest, Media, People, Lists，[可选]，示例: Top")] = None,
                          cursor: Annotated[Optional[str], Field(description="分页游标，首次不传，后续从上一次返回结果中获取，[可选]")] = None) -> Dict[str, Any]:
    """X(Twitter) 关键词搜索推文。keyword 必填；
    search_type：Top/Latest/Media/People/Lists；cursor 用于翻页。

接口: POST /story/api/x/search"""
    return call(lambda: get_client().twitter.search_tweets,
                keyword=keyword, search_type=search_type, cursor=cursor, source="X(Twitter) 关键词搜索推文-MCP")


@mcp.tool()
def twitter_get_tweet(tweet_id: Annotated[str, Field(description="推文ID，[必填]，示例: 2076962843841470561")]) -> Dict[str, Any]:
    """获取 X(Twitter) 单条推文详情。tweet_id 为推文 ID（必填）。

接口: POST /story/api/x/tweetDetail"""
    return call(lambda: get_client().twitter.get_tweet, tweet_id=tweet_id, source="获取 X(Twitter) 单条推文详情-MCP")


@mcp.tool()
def twitter_get_user(screen_name: Annotated[Optional[str], Field(description="用户名（如 maurodm600），[可选]，示例: elonmusk")] = None,
                     rest_id: Annotated[Optional[str], Field(description="用户ID（如 110766540），传入后会忽略 screenName，[可选]")] = None) -> Dict[str, Any]:
    """获取 X(Twitter) 用户信息。screen_name 与 rest_id 至少传一个。

接口: POST /story/api/x/userInfo"""
    return call(lambda: get_client().twitter.get_user,
                screen_name=screen_name, rest_id=rest_id, source="获取 X(Twitter) 用户信息-MCP")


@mcp.tool()
def twitter_get_comments(tweet_id: Annotated[str, Field(description="推文ID，[必填]，示例: 2076962843841470561")],
                         cursor: Annotated[Optional[str], Field(description="游标，默认为None，用于翻页，后续从上一次请求的返回结果中获取，[可选]")] = None) -> Dict[str, Any]:
    """获取 X(Twitter) 推文评论/回复。tweet_id 必填；cursor 用于翻页。

接口: POST /story/api/x/tweetComments"""
    return call(lambda: get_client().twitter.get_comments,
                tweet_id=tweet_id, cursor=cursor, source="获取 X(Twitter) 推文评论/回复-MCP")


def main() -> None:
    serve(mcp, prog="redfox-twitter-mcp", description="RedFox X(Twitter) MCP server")


if __name__ == "__main__":
    main()
