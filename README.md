# 基于 [Saiblo 平台](https://www.saiblo.net/)的黑白棋 AI

黑白棋（Reversi，又名翻转棋）是简单有趣的小游戏，其详细规则可见 [维基百科](https://zh.wikipedia.org/zh-cn/%E9%BB%91%E7%99%BD%E6%A3%8B)、[百度百科](https://baike.baidu.com/item/%E9%BB%91%E7%99%BD%E6%A3%8B/80689)。

1. 棋盘大小 8 * 8，棋子分黑白
2. 初始位置黑子：e4, d5，白子：d4, e5。黑先
3. 当一方落子后，夹在己方棋子中间的对方棋子就会被吃掉（8个方向），然后翻转变为己方颜色，双方交替落子
4. 当一方无子可落时，由对方落子；双方均无子可落时游戏结束
5. 终盘子数多的一方获胜


## 平台

**警告：代码仅做学习参考用，请上交自己独立写出的代码！**

黑白棋 AI 的评测在 [Saiblo 平台](https://www.saiblo.net/) 上进行。


比赛不需要人工干预，系统自动每隔一段时间对所有 AI 进行天梯排位（使用 [ELO 等级分](https://zh.wikipedia.org/wiki/%E7%AD%89%E7%BA%A7%E5%88%86) 进行计算）。刷新比赛页面即可看到目前已经进行的战局，同样可以进行回放。点击右侧“查看排行榜”可看到目前的 AI 排名，并可以与任意一个 AI 发起一个快速人机战局，或者复制其 token 在房间中使用。

## 代码组成

基本思路：给棋盘局面打分，穷举可能的情况，得到最优解；在本代码中使用了 [alpha-beta 剪枝](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning) 来进行搜索。

将棋盘作为一个类来处理：

### 变量

* 执棋手 `_id`：0 代表黑，1 代表白

* 棋盘 `_board`：长 64 的 `list`，0 代表黑，1 代表白，2 代表空

* 某一格是否可下的信息 `_feasible`：8 个方向，`0b00000000` 8 位存储可行的方向信息

### 成员函数

* 估值函数 `value`：赋予每个格子一个权重，输出 = 己方 - 对方加权和，这样就是一个**零和博弈**

* 判断函数 `feasible`：输入某一格坐标，将可行方向的信息存储在 `self._feasible` 中，再输出是否可落子的布尔值

* 下棋函数 `play`：输入落子格坐标，按规则翻转棋子，输出新的棋盘对象

* alpha-beta 剪枝函数 `alpha_beta`：输入 `depth, alpha, beta, AI_turn`，执行 alpha-beta 剪枝，输出当前棋盘的最优值

### AI 函数

尝试下当前所有可下的格子，比较落子后各棋盘的 alpha-beta 输出值，取最大值对应的格子

## 心得

1. 与其去纠结权重表某一处参数的大小取值，不如优化搜索效率。

2. 在演化棋盘的时候应当自己实现 `ask_next_pos(choice: int)`（在我的代码中即判断函数），因为使用原有的 `ask_next_pos` 并不能正确的把握 3s 的时机，导致不能充分利用或 TLE

3. 估值函数不能仅凭一个常数权重表，<u>在终局肯定是计算子数多少</u>。我还加入了[稳定子](http://www.soongsky.com/othello/strategy/stable.php)判断，但是没有加[行动力](http://www.soongsky.com/othello/strategy/mobility.php)等的判断，因为我认为这些都包含在了穷举之中

4. 一个小 trick：判断函数若仅输出布尔值会丢失信息，而在后面下棋函数翻转棋子也需要判断哪个方向可行，所以我在类中额外设置了 `Reversi._feasible` 避免重复的判断

5. 若将 `list` 改为 `np.ndarray` 并优化相关 `for` 循环，可想而知，效率可以更优，~~只是我懒得弄了~~

## 附：有用的网站

1. [黑白棋天地](http://www.soongsky.com/othello/)：基本策略和电脑黑白棋栏较为有用

2. Saiblo 类似平台：隔壁的 [Botzone](https://botzone.org.cn/)，里面甚至有部分选手主动公开的源码（当然了Saiblo 高分得主很多也上传到自己的 github 上了）

3. 最强的黑白棋之一：[WZebra](http://radagast.se/othello/download.html)

4. 当前榜一 frvdec 的 MINIMAX v.13 的 [github 地址](https://github.com/frvdecQAQ/reversi)；榜二 Dixiao-Lew 的 Null v.9 的 [github 地址](https://github.com/Dixiao-L/othello)