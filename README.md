# 黑白棋 AI

## 背景

黑白棋（Reversi，又名翻转棋）是简单有趣的小游戏，其详细规则可见 [维基百科](https://zh.wikipedia.org/zh-cn/%E9%BB%91%E7%99%BD%E6%A3%8B)、[百度百科](https://baike.baidu.com/item/%E9%BB%91%E7%99%BD%E6%A3%8B/80689)。


## 平台

黑白棋 AI 的评测完全在 [Saiblo 平台](https://www.saiblo.net/) 上进行。


比赛不需要人工干预，系统自动每隔一段时间对所有 AI 进行天梯排位（使用 [ELO 等级分](https://zh.wikipedia.org/wiki/%E7%AD%89%E7%BA%A7%E5%88%86) 进行计算）。刷新比赛页面即可看到目前已经进行的战局，同样可以进行回放。点击右侧“查看排行榜”可看到目前的 AI 排名，并可以与任意一个 AI 发起一个快速人机战局，或者复制其 token 在房间中使用。

## 代码组成

* 类：棋盘。其中有下棋函数、估值函数和判断可落点的函数
* alpha-beta 剪枝函数
* ai 函数，判断下哪一步