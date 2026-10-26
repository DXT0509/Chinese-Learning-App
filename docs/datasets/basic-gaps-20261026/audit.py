"""Read-only, bounded beginner-vocabulary coverage audit; not an official HSK list."""

import asyncio
import json
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings
from app.core.event_loop import new_event_loop
from app.models.curated_vocabulary import CuratedVocabulary

GROUPS = {
    "characters": "女 口 男 子 人 大 小 上 下 中 左 右 前 后 东 西 南 北 一 二 三 四 五 六 七 八 九 十 百 千 万 零 两 日 月 年 天 时 分 秒 今 明 昨 早 晚 午 半 星 水 火 木 金 土 山 石 田 云 雨 风 雪 电 气 光 米 面 肉 鱼 鸟 虫 马 牛 羊 狗 猫 鸡 鸭 猪 兔 龙 鼠 虎 蛇 手 足 脚 头 目 眼 耳 鼻 嘴 牙 心 身 皮 血 毛 见 看 听 说 读 写 学 问 答 认 识 知 道 想 会 能 要 有 是 在 住 去 来 回 进 出 开 关 起 坐 站 走 跑 跳 吃 喝 买 卖 给 用 做 打 找 等 叫 让 帮 爱 喜 欢 笑 哭 唱 玩 睡 醒 穿 脱 洗 送 拿 放 带 还 先 再 又 都 也 很 不 没 太 更 最 真 多 少 几 这 那 哪 谁 的 地 得 了 过 着 吗 呢 吧 啊 和 跟 对 从 到 把 被 比 个 本 张 只 条 件 杯 瓶 碗 双 次 岁 块 元 角 钱 斤 克 里 长 短 高 矮 胖 瘦 好 坏 新 旧 冷 热 快 慢 远 近 轻 重 贵 难 易 忙 累 饿 渴 病 疼 对 错 红 黄 蓝 绿 白 黑 爸 妈 哥 姐 弟 妹 儿 孙 家 房 门 窗 床 桌 椅 书 笔 纸 包 车 路 店 市 站 国 生 老 师 友 朋 名 字 文 汉 语 课 班 校 工 作 力",
    "people": "我们 你们 他们 她们 它 它们 大家 别人 自己 男孩 女孩 男人 女人 男生 女生 男朋友 女朋友 孩子 儿子 女儿 父亲 母亲 爸爸 妈妈 哥哥 姐姐 弟弟 妹妹 爷爷 奶奶 外公 外婆 丈夫 妻子 先生 太太 家人 朋友 同学 同事 学生 老师 医生 护士 司机 服务员 老人 年轻人",
    "body": "身体 眼睛 耳朵 鼻子 嘴巴 头发 牙齿 肚子 胳膊 腿 脚趾 手指 脖子 脸 膝盖 头疼 感冒 生病 健康 医院 药 药店",
    "time": "今天 明天 昨天 现在 时候 时间 早上 上午 中午 下午 晚上 白天 夜里 晚安 星期 周末 周一 星期一 星期二 星期三 星期四 星期五 星期六 星期日 星期天 今年 明年 去年 生日 小时 分钟 秒钟 点 半 夜 今天晚上 以前 以后 刚才 马上 已经 正在 还没 一会儿 每天 每年 每月 每周 有时候 常常 从来 一起",
    "home": "房子 房间 卧室 客厅 厨房 洗手间 卫生间 门口 窗户 桌子 椅子 床上 冰箱 电视 电脑 手机 电话 空调 洗衣机 灯 水杯 杯子 瓶子 碗筷 盘子 勺子 筷子 书包 包 皮包 钱包 钥匙 衣服 裤子 裙子 鞋 袜子 帽子 眼镜 伞 雨伞 毛巾 牙刷 牙膏 肥皂 洗澡 洗脸 刷牙 起床 睡觉 开门 关门",
    "food": "米饭 面条 馒头 饺子 包子 面包 鸡蛋 牛奶 豆浆 茶 咖啡 水 果汁 啤酒 白酒 饮料 开水 热水 冷水 水果 苹果 香蕉 橘子 橙子 葡萄 西瓜 草莓 桃子 梨 蔬菜 白菜 西红柿 土豆 黄瓜 胡萝卜 鸡肉 牛肉 猪肉 羊肉 鱼肉 汤 盐 糖 油 醋 辣椒 早餐 午饭 晚饭 早饭 饭店 餐厅 菜单 好吃 好喝 饱 饿 渴 甜 咸 酸 苦 辣",
    "places": "学校 教室 图书馆 商店 超市 市场 银行 邮局 公园 车站 火车站 地铁站 机场 电影院 酒店 宾馆 中国 越南 北京 河内 胡志明市 中文 汉语 越南语 英语 公共汽车 出租车 自行车 摩托车 汽车 火车 飞机 地铁 轮船 马路 红绿灯 路口 旁边 对面 外面 里面 上面 下面 前面 后面 左边 右边 附近 这里 那里 哪里",
    "actions": "学习 工作 上班 下班 上学 放学 上课 下课 复习 练习 考试 作业 汉字 拼音 声调 发音 写字 读书 看书 唱歌 跳舞 跑步 游泳 走路 开车 骑车 坐车 打车 打电话 上网 聊天 照相 拍照 买东西 购物 付钱 找钱 帮忙 休息 旅行 旅游 散步 运动 打球 踢足球 打篮球 打开 关闭 进入 出去 回来 回家 看见 听见 知道 认识 觉得 喜欢 希望 需要 应该 可以 可能 必须 准备 开始 结束 带来 拿走 等等 参加 回答 告诉 介绍",
    "descriptions": "漂亮 好看 高兴 快乐 开心 难过 生气 害怕 紧张 安静 干净 脏 便宜 昂贵 容易 困难 简单 复杂 重要 方便 舒服 热闹 热情 认真 聪明 可爱 年轻 满 空 一样 不同 正确 错误 非常 有点儿 一点儿 多少 为什么 怎么 怎么样 哪个 哪儿 这儿 那儿 没有 不是 不用 不会 不要 不能 不可以 因为 所以 但是 可是 然后 如果 虽然 还是 或者 而且",
}


async def run():
    root = Path(__file__).resolve().parent
    original = root.parent / "codex-review-4.0.3" / "provisional-deployment.jsonl"
    reserved = {
        json.loads(line)["simplified"] for line in original.read_text(encoding="utf-8").splitlines()
    }
    candidates = {group: list(dict.fromkeys(forms.split())) for group, forms in GROUPS.items()}
    engine = create_async_engine(get_settings().database_url, echo=False)
    try:
        async with engine.connect() as connection, connection.begin():
            await connection.execute(
                text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
            )
            async with AsyncSession(connection) as session:
                words = list(await session.scalars(select(CuratedVocabulary)))
                forms = {word.simplified for word in words}
                missing = {
                    g: [w for w in values if w not in forms and w not in reserved]
                    for g, values in candidates.items()
                }
                pending = {
                    g: [w for w in values if w not in forms and w in reserved]
                    for g, values in candidates.items()
                }
                report = {
                    "scope": "Session-curated beginner checklist, not an exhaustive or official HSK list",
                    "database": list(
                        (
                            await session.execute(
                                text(
                                    "SELECT current_database(), inet_server_addr()::text, inet_server_port(), current_user"
                                )
                            )
                        ).one()
                    ),
                    "catalog_records": len(words),
                    "checked_unique_forms": len(
                        {w for values in candidates.values() for w in values}
                    ),
                    "candidate_groups": candidates,
                    "missing_forms": missing,
                    "reserved_source_forms_not_in_database": pending,
                    "all_existing_catalog_forms": sorted(forms),
                    "database_writes": 0,
                }
                (root / "coverage-scan.json").write_text(
                    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                print(
                    json.dumps(
                        {
                            k: report[k]
                            for k in (
                                "catalog_records",
                                "checked_unique_forms",
                                "missing_forms",
                                "reserved_source_forms_not_in_database",
                            )
                        },
                        ensure_ascii=False,
                    )
                )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    with asyncio.Runner(loop_factory=new_event_loop) as runner:
        runner.run(run())
