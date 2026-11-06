# 站点主题 · 真实浏览器验收

> 2026-11-06 · Chrome headless `--dump-dom` + `getComputedStyle`，本地 IPv6 `::1` HTTP 服务。
> 场景 A：全新 profile 首次访问，检查默认深色与配色中性，再点击切换按钮。
> 场景 B：同一 `--user-data-dir` 二次访问，检查主题偏好是否记忆。

**结果：13 项通过，0 项失败**

| 场景 | 断言结果 |
| --- | --- |
| A 首次访问 | default_dark=PASS；btn_says_switch_to_light=PASS(浅色)；dark_bg_is_dark=PASS(17,20,24)；dark_bg_not_green=PASS(17,20,24)；accent_not_green=PASS(143,185,224)；overlay_not_green=PASS(12,16,21)；toggle_to_light=PASS；btn_says_switch_to_dark=PASS(深色)；light_bg_is_bright=PASS(247,248,250)；light_bg_not_green=PASS(247,248,250)；preference_saved=PASS(light) |
| B 二次访问 | remembered_light=PASS(light)；btn_label=PASS(深色) |

## 口径

- 「无绿偏」= `getComputedStyle` 取到的 RGB 中，G 通道不大于 max(R,B)。
  原深色的 `#151a17` / `#1d241f` / `#79c8a2` 等全部 G 通道主导，故整页泛绿。
- 绿色点缀已换成石板蓝（浅色 `#3b6d9e` / 深色 `#8fb9e0`），两套主题同色系。
- 默认深由 `<html data-theme="dark">` 保证，首帧无闪白；显式切浅色后由
  `localStorage` 记忆，隐私模式或 `file://` 下静默回落到深色。
- 本报告只验证渲染与交互，不证明新闻事实为真。
