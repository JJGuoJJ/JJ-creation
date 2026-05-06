{
  "brand_attributes": {
    "personality": [
      "高端投行/对冲基金内部系统",
      "高信息密度但可读",
      "冷静克制、强对比、强层级",
      "以数据为主角（数字/表格/图表优先）",
      "中文为主，代码/股票代码英文"
    ],
    "north_star": "3 秒内看清：市场阶段→情绪→仓位建议→今日动作→关键风险信号；其余信息按需展开。"
  },
  "design_tokens": {
    "notes": [
      "默认深色模式（.dark），提供浅色模式切换。",
      "避免大面积渐变；渐变仅用于 hero/装饰（<= 20% 视口）。",
      "数字与表格使用等宽字体，提升扫读与对齐。"
    ],
    "typography": {
      "google_fonts": [
        {
          "family": "IBM Plex Sans",
          "weights": ["400", "500", "600", "700"],
          "usage": "中文 UI 主体（标题/正文/标签）"
        },
        {
          "family": "IBM Plex Mono",
          "weights": ["400", "500", "600"],
          "usage": "数字、代码、ticker、表格数值列"
        }
      ],
      "font_stack": {
        "sans": "\"IBM Plex Sans\", ui-sans-serif, system-ui, -apple-system, \"Segoe UI\", \"PingFang SC\", \"Hiragino Sans GB\", \"Microsoft YaHei\", sans-serif",
        "mono": "\"IBM Plex Mono\", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace"
      },
      "scale_tailwind": {
        "h1": "text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight",
        "h2": "text-base md:text-lg font-medium text-muted-foreground",
        "section_title": "text-sm font-semibold tracking-wide",
        "body": "text-sm md:text-base leading-6",
        "caption": "text-xs text-muted-foreground",
        "numeric_kpi": "font-mono tabular-nums text-2xl md:text-3xl font-semibold",
        "numeric_cell": "font-mono tabular-nums text-sm"
      },
      "chinese_readability": {
        "line_height": "中文正文建议 leading-6~7；表格行高紧凑但不挤（h-10~11）。",
        "punctuation": "中文标点与英文 ticker 混排时，ticker 用 font-mono + tracking-tight。"
      }
    },
    "spacing": {
      "baseline": "8px",
      "container": "px-4 sm:px-6 lg:px-8",
      "section_gap": "gap-6 lg:gap-8",
      "card_padding": "p-4 md:p-5",
      "dense_table": "row h-10, cell px-3"
    },
    "radius": {
      "global": "--radius: 10px (override from 0.5rem)",
      "card": "rounded-xl",
      "chip": "rounded-full",
      "table": "rounded-lg"
    },
    "shadows": {
      "dark_mode": {
        "card": "shadow-[0_1px_0_rgba(255,255,255,0.06),0_12px_30px_rgba(0,0,0,0.35)]",
        "popover": "shadow-[0_10px_30px_rgba(0,0,0,0.55)]"
      },
      "light_mode": {
        "card": "shadow-[0_1px_0_rgba(0,0,0,0.04),0_12px_30px_rgba(15,23,42,0.10)]",
        "popover": "shadow-[0_10px_30px_rgba(15,23,42,0.18)]"
      }
    },
    "color_system": {
      "mode": "dual",
      "dark": {
        "background": "222 47% 6%",
        "foreground": "210 40% 98%",
        "card": "222 44% 8%",
        "card_foreground": "210 40% 98%",
        "muted": "222 28% 14%",
        "muted_foreground": "215 20% 70%",
        "border": "222 22% 18%",
        "input": "222 22% 18%",
        "ring": "188 92% 42%",
        "primary": "188 92% 42%",
        "primary_foreground": "222 47% 6%",
        "secondary": "222 28% 14%",
        "secondary_foreground": "210 40% 98%",
        "accent": "222 28% 14%",
        "accent_foreground": "210 40% 98%",
        "destructive": "0 72% 52%",
        "destructive_foreground": "210 40% 98%",
        "focus": "188 92% 42%",
        "surface_1": "222 44% 8%",
        "surface_2": "222 34% 10%",
        "surface_3": "222 28% 14%",
        "ticker_strip": "222 47% 6%",
        "gridline": "222 22% 18%"
      },
      "light": {
        "background": "210 40% 98%",
        "foreground": "222 47% 11%",
        "card": "0 0% 100%",
        "card_foreground": "222 47% 11%",
        "muted": "210 30% 96%",
        "muted_foreground": "215 16% 40%",
        "border": "214 20% 88%",
        "input": "214 20% 88%",
        "ring": "188 92% 34%",
        "primary": "188 92% 34%",
        "primary_foreground": "0 0% 100%",
        "secondary": "210 30% 96%",
        "secondary_foreground": "222 47% 11%",
        "accent": "210 30% 96%",
        "accent_foreground": "222 47% 11%",
        "destructive": "0 72% 52%",
        "destructive_foreground": "0 0% 100%",
        "focus": "188 92% 34%",
        "surface_1": "0 0% 100%",
        "surface_2": "210 30% 96%",
        "surface_3": "214 20% 92%",
        "ticker_strip": "210 40% 98%",
        "gridline": "214 20% 88%"
      },
      "semantic": {
        "info": "199 89% 48%",
        "warning": "38 92% 50%",
        "success": "158 64% 42%",
        "danger": "0 72% 52%",
        "neutral": "215 16% 60%"
      },
      "gradients_allowed": {
        "hero_bg": "radial-gradient(1200px circle at 20% 10%, rgba(20,184,166,0.18), transparent 55%), radial-gradient(900px circle at 80% 0%, rgba(56,189,248,0.10), transparent 50%)",
        "restriction": "渐变覆盖面积 <= 20% 视口；仅用于页面顶部装饰层，不覆盖阅读区域。"
      },
      "texture": {
        "noise_overlay": {
          "css": "background-image: url('data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" width=\"160\" height=\"160\"%3E%3Cfilter id=\"n\"%3E%3CfeTurbulence type=\"fractalNoise\" baseFrequency=\"0.8\" numOctaves=\"3\" stitchTiles=\"stitch\"/%3E%3C/filter%3E%3Crect width=\"160\" height=\"160\" filter=\"url(%23n)\" opacity=\"0.06\"/%3E%3C/svg%3E');",
          "usage": "在 app 背景或 hero 装饰层叠加（pointer-events-none），避免影响文本清晰度。"
        }
      }
    },
    "data_viz_palette": {
      "principles": [
        "避免彩虹色；同类指标用同色系不同明度。",
        "深色模式下线条更细（stroke 1.5~2），点更小（r 2）。",
        "图表背景保持透明，依赖 card/surface。"
      ],
      "categorical_6": [
        {"name": "teal", "hex": "#14B8A6"},
        {"name": "sky", "hex": "#38BDF8"},
        {"name": "amber", "hex": "#F59E0B"},
        {"name": "lime", "hex": "#84CC16"},
        {"name": "rose", "hex": "#F43F5E"},
        {"name": "slate", "hex": "#94A3B8"}
      ],
      "sequential_heat": {
        "hotness": ["#0B1220", "#0EA5A4", "#22C55E", "#F59E0B"],
        "risk": ["#0B1220", "#38BDF8", "#F59E0B", "#EF4444"],
        "fear_greed": ["#EF4444", "#F59E0B", "#94A3B8", "#22C55E"]
      }
    }
  },
  "market_color_rules": {
    "default_convention": "CN",
    "cn": {
      "up": {"label": "涨", "text": "text-red-400", "bg": "bg-red-500/10", "stroke": "#F87171"},
      "down": {"label": "跌", "text": "text-emerald-400", "bg": "bg-emerald-500/10", "stroke": "#34D399"},
      "flat": {"label": "平", "text": "text-slate-300", "bg": "bg-slate-500/10", "stroke": "#CBD5E1"}
    },
    "us": {
      "up": {"label": "涨", "text": "text-emerald-400", "bg": "bg-emerald-500/10", "stroke": "#34D399"},
      "down": {"label": "跌", "text": "text-red-400", "bg": "bg-red-500/10", "stroke": "#F87171"},
      "flat": {"label": "平", "text": "text-slate-300", "bg": "bg-slate-500/10", "stroke": "#CBD5E1"}
    },
    "implementation": {
      "rule": "每个标的/指数必须带 market 标记（CN/US/Crypto）。渲染涨跌色时按 market 选择映射。",
      "testid": "data-testid=\"market-color-convention-toggle\""
    }
  },
  "layout_system": {
    "app_shell": {
      "pattern": "Bloomberg-like split layout",
      "structure": [
        "顶部：紧凑 Header（含全局搜索、更新时间、模式切换、用户菜单）",
        "左侧：可折叠 Sidebar（7 个页面入口 + 快捷筛选）",
        "主区：可滚动内容（卡片网格 + 表格 + 图表）"
      ],
      "sidebar": {
        "width": "w-[260px] (expanded), w-[72px] (collapsed)",
        "behavior": "桌面默认展开；移动端用 Sheet 抽屉。",
        "nav_item": "左侧图标 + 中文标题；当前页高亮用左侧 2px accent bar。"
      },
      "grid": {
        "desktop": "12 columns, gap-6",
        "overview": "上方 12 列：Market Phase(4) + F&G(4) + 综合分/风险(4)；下方：仓位建议(6) + 今日动作(6)；再下：热力图(8) + 风险信号(4)",
        "mobile": "单列堆叠；关键 KPI 卡置顶；表格横向滚动。"
      }
    },
    "density_modes": {
      "default": "Comfort",
      "options": [
        {
          "name": "Comfort",
          "table": "h-11 px-3",
          "cards": "p-5",
          "testid": "data-testid=\"density-mode-comfort\""
        },
        {
          "name": "Dense",
          "table": "h-10 px-2.5",
          "cards": "p-4",
          "testid": "data-testid=\"density-mode-dense\""
        }
      ]
    }
  },
  "page_layouts": {
    "overview": {
      "route": "/",
      "goal": "一屏完成：阶段→情绪→仓位→动作→风险",
      "sections": [
        {
          "name": "Top KPI Grid",
          "layout": "grid grid-cols-1 lg:grid-cols-12 gap-6",
          "blocks": [
            "Market Phase 阶段卡（lg:col-span-4）",
            "Fear & Greed 三联卡（lg:col-span-4）",
            "综合分 + 关键风险信号摘要（lg:col-span-4）"
          ]
        },
        {
          "name": "Action + Allocation",
          "layout": "grid grid-cols-1 lg:grid-cols-12 gap-6",
          "blocks": [
            "仓位建议环形图 + 目标权重列表（lg:col-span-7）",
            "今日操作建议卡（lg:col-span-5）：动作徽章 + 原因解释 + 触发条件"
          ]
        },
        {
          "name": "Signals",
          "layout": "grid grid-cols-1 lg:grid-cols-12 gap-6",
          "blocks": [
            "赛道热度热力图（lg:col-span-8）",
            "关键风险信号列表（lg:col-span-4）：宏观/流动性/波动率/政策"
          ]
        }
      ],
      "micro_interactions": [
        "数值更新：背景轻微闪烁 120ms（up/down 颜色），避免强动画。",
        "卡片 hover：border 提亮 + ring-1 ring-primary/20。",
        "热力图 cell hover：tooltip 展示因子与解释。"
      ]
    },
    "portfolio": {
      "route": "/portfolio",
      "sections": [
        "顶部：组合摘要条（净敞口/总敞口/现金/当日PnL）",
        "中部：当前持仓表（可排序/筛选/固定表头/横向滚动）",
        "右侧或下方：按赛道饼图 + 权重 vs 建议权重对比条形图",
        "底部：应加仓/应减仓列表（带原因解释与优先级）"
      ],
      "table_specs": {
        "columns": [
          "代码/名称",
          "市场(CN/US/Crypto)",
          "赛道",
          "成本/现价",
          "持仓权重",
          "建议权重",
          "偏离度",
          "当日PnL",
          "累计PnL",
          "风险标记"
        ],
        "row_behavior": "点击行展开 Drawer：展示诊断（偏离原因、技术指标、建议动作、止损/加仓区间）",
        "testids": {
          "table": "data-testid=\"portfolio-holdings-table\"",
          "row": "data-testid=\"portfolio-holdings-row\"",
          "filter": "data-testid=\"portfolio-filter-bar\""
        }
      }
    },
    "sectors": {
      "route": "/sectors",
      "sections": [
        "顶部：筛选（市场/风险偏好/时间窗）+ 搜索",
        "主体：赛道卡片网格（2~3 列），每卡包含：热度分、风险分、20日均涨幅、量比、RSI、趋势小图、动作建议",
        "卡片点击：进入赛道详情 Drawer（成分股Top、因子贡献、风险提示）"
      ],
      "card_density": "卡片内部采用两列信息栅格：左侧分数/徽章，右侧 mini sparkline。"
    },
    "watchlist": {
      "route": "/watchlist",
      "sections": [
        "顶部：可组合筛选（赛道、动作、得分区间、市场）+ 快捷 chips",
        "主体：观察池排名表（高密度）",
        "行展开：HoverCard/Collapsible 展示原因解释、关键技术指标、最近信号"
      ],
      "interaction": "表格行 hover 显示右侧操作：加入持仓/设提醒/打开详情。"
    },
    "fear_greed": {
      "route": "/sentiment",
      "sections": [
        "顶部：三条曲线（Global/China Tech/Crypto）可切换时间窗（1M/3M/6M/YTD）",
        "中部：因子贡献分解图（堆叠条形或瀑布图）",
        "底部：解释区（Markdown）：今日情绪变化原因与可执行动作"
      ]
    },
    "reports": {
      "route": "/reports",
      "layout": "Resizable split pane",
      "sections": [
        "左侧：报告列表（按日期，支持搜索/标签：宏观/科技/加密/黄金）",
        "右侧：Markdown 阅读器（目录锚点、代码块、引用块、关键结论高亮）",
        "顶部工具条：下载、复制摘要、标记已读"
      ],
      "reader_specs": {
        "typography": "正文 text-sm leading-7；标题使用 font-sans font-semibold；数字/代码块 font-mono",
        "callouts": "关键结论用 Alert 组件（info/warning/success）",
        "testids": {
          "list": "data-testid=\"reports-list\"",
          "viewer": "data-testid=\"reports-markdown-viewer\"",
          "download": "data-testid=\"reports-download-button\""
        }
      }
    },
    "settings": {
      "route": "/settings",
      "sections": [
        "风险偏好：RadioGroup（保守/平衡/进取）",
        "策略阈值：Form + Slider/Input（F&G 阈值、最大回撤、单赛道上限）",
        "持股数量录入：可编辑表格（代码、数量、成本）",
        "观察池管理：添加/删除/导入（CSV）"
      ],
      "testids": {
        "risk": "data-testid=\"settings-risk-profile\"",
        "thresholds": "data-testid=\"settings-strategy-thresholds\"",
        "holdings": "data-testid=\"settings-holdings-editor\""
      }
    }
  },
  "key_components_specs": {
    "fear_greed_gauge_card": {
      "description": "三联 Fear & Greed 数字仪表卡（Global/China Tech/Crypto），强调数值与变化。",
      "layout": "Card -> header(标题+更新时间) + body(大数字+刻度条/半环) + footer(解释一句话)",
      "visual": {
        "number": "font-mono tabular-nums text-3xl",
        "scale": "Progress/自定义半环；颜色按 fear_greed sequential",
        "badge": "Badge：Fear/Neutral/Greed"
      },
      "states": {
        "loading": "Skeleton（数字块 + 条形）",
        "hover": "ring-1 ring-primary/20 + border 提亮",
        "focus": "focus-visible:ring-2 ring-ring"
      },
      "testids": {
        "card": "data-testid=\"fear-greed-gauge-card\"",
        "value": "data-testid=\"fear-greed-value\""
      }
    },
    "market_phase_card": {
      "description": "Market Phase 阶段卡：阶段名称 + 置信度 + 关键驱动因子。",
      "visual": {
        "phase_badge": "Badge variant=secondary + 左侧 6px 色条",
        "confidence": "Progress + 数值（font-mono）",
        "drivers": "3 条 bullet（muted 文本）"
      },
      "testids": {
        "card": "data-testid=\"market-phase-card\""
      }
    },
    "allocation_donut": {
      "description": "仓位建议环形图 + 目标权重列表（右侧 legend 可点击高亮）。",
      "recharts": {
        "component": "PieChart + Pie + Cell + Tooltip + Legend(custom)",
        "donut": "innerRadius=60 outerRadius=90 paddingAngle=2",
        "label": "中心显示：风险等级 + 现金比例（font-mono）"
      },
      "testids": {
        "chart": "data-testid=\"allocation-donut-chart\""
      }
    },
    "heat_score_bar": {
      "description": "赛道热度条（0-100）：左侧名称，右侧条形 + 数值 + 动作徽章。",
      "visual": {
        "bar": "Progress 组件 + 自定义渐变（仅条内，不算 viewport 渐变限制）",
        "value": "font-mono",
        "action_badge": "Badge：加仓/观望/减仓/回避"
      },
      "testids": {
        "row": "data-testid=\"sector-heat-score-row\""
      }
    },
    "action_badge": {
      "variants": {
        "add": {"label": "加仓", "classes": "bg-emerald-500/15 text-emerald-300 border border-emerald-500/25"},
        "hold": {"label": "观望", "classes": "bg-slate-500/15 text-slate-200 border border-slate-500/25"},
        "trim": {"label": "减仓", "classes": "bg-amber-500/15 text-amber-300 border border-amber-500/25"},
        "avoid": {"label": "回避", "classes": "bg-red-500/15 text-red-300 border border-red-500/25"}
      },
      "micro": "hover:brightness-110; active:scale-[0.98]（仅按钮/可点击徽章）",
      "testid": "data-testid=\"action-badge\""
    },
    "recommendation_row": {
      "description": "推荐表格行：左侧 ticker + 赛道，中间得分/动作，右侧原因（可展开）。",
      "behavior": [
        "默认显示原因前 1 行，点击展开 Collapsible 显示完整原因与指标",
        "行 hover 显示右侧快捷操作（加入持仓/设提醒）"
      ],
      "visual": {
        "row": "border-b border-border/70 hover:bg-muted/40",
        "reason": "text-xs text-muted-foreground line-clamp-1"
      },
      "testids": {
        "row": "data-testid=\"recommendation-table-row\"",
        "expand": "data-testid=\"recommendation-row-expand\""
      }
    },
    "dense_data_table": {
      "description": "高密度表格（持仓/观察池通用）：固定表头、可排序、可筛选、横向滚动。",
      "visual": {
        "header": "sticky top-0 bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/70",
        "cell": "px-3 py-2 text-sm",
        "numeric": "text-right font-mono tabular-nums",
        "divider": "border-border/70"
      },
      "performance": {
        "recommendation": "若行数>200，建议引入虚拟滚动（react-virtual）。MVP 可先不做。"
      },
      "testids": {
        "table": "data-testid=\"dense-data-table\""
      }
    }
  },
  "component_path": {
    "shadcn_ui": [
      "/app/frontend/src/components/ui/button.jsx",
      "/app/frontend/src/components/ui/card.jsx",
      "/app/frontend/src/components/ui/badge.jsx",
      "/app/frontend/src/components/ui/table.jsx",
      "/app/frontend/src/components/ui/tabs.jsx",
      "/app/frontend/src/components/ui/scroll-area.jsx",
      "/app/frontend/src/components/ui/resizable.jsx",
      "/app/frontend/src/components/ui/sheet.jsx",
      "/app/frontend/src/components/ui/dropdown-menu.jsx",
      "/app/frontend/src/components/ui/select.jsx",
      "/app/frontend/src/components/ui/tooltip.jsx",
      "/app/frontend/src/components/ui/hover-card.jsx",
      "/app/frontend/src/components/ui/collapsible.jsx",
      "/app/frontend/src/components/ui/separator.jsx",
      "/app/frontend/src/components/ui/progress.jsx",
      "/app/frontend/src/components/ui/skeleton.jsx",
      "/app/frontend/src/components/ui/switch.jsx",
      "/app/frontend/src/components/ui/calendar.jsx",
      "/app/frontend/src/components/ui/dialog.jsx",
      "/app/frontend/src/components/ui/drawer.jsx",
      "/app/frontend/src/components/ui/sonner.jsx"
    ],
    "charts": {
      "library": "Recharts (already present)",
      "components": ["LineChart", "AreaChart", "PieChart", "BarChart", "ResponsiveContainer", "Tooltip", "Legend"]
    }
  },
  "libraries": {
    "recommended": [
      {
        "name": "framer-motion",
        "why": "用于页面进入、卡片 hover、chip 移除等微动效（可控且不影响性能）",
        "install": "npm i framer-motion",
        "usage": "仅用于关键交互：Sidebar 展开、卡片入场、Collapsible 展开。避免全局动画。"
      },
      {
        "name": "react-markdown + remark-gfm",
        "why": "报告页 Markdown 渲染（表格/任务列表/链接）",
        "install": "npm i react-markdown remark-gfm",
        "usage": "Reports viewer：自定义组件映射到 shadcn 的 Typography/Alert/Table。"
      }
    ]
  },
  "image_urls": {
    "background_texture_optional": [
      {
        "url": "https://images.unsplash.com/photo-1650488908294-07186d808e5d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMjd8MHwxfHNlYXJjaHwxfHxzdWJ0bGUlMjBncmFpbiUyMHRleHR1cmUlMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8dGVhbHwxNzc4MDUwOTIzfDA&ixlib=rb-4.1.0&q=85",
        "category": "app-shell",
        "description": "可选：作为极淡的背景纹理参考（不建议直接铺满；优先用 CSS noise overlay）。"
      },
      {
        "url": "https://images.unsplash.com/photo-1626196295010-82e53396c9d1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMjd8MHwxfHNlYXJjaHwyfHxzdWJ0bGUlMjBncmFpbiUyMHRleHR1cmUlMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8dGVhbHwxNzc4MDUwOTIzfDA&ixlib=rb-4.1.0&q=85",
        "category": "reports",
        "description": "可选：报告页封面/空状态背景纹理参考（建议裁切并降低不透明度）。"
      }
    ]
  },
  "instructions_to_main_agent": {
    "global_css_updates": [
      "在 /app/frontend/src/index.css 覆盖 :root 与 .dark 的 HSL token（见 design_tokens.color_system）。",
      "将 --radius 调整为 10px（更像投行系统的精致圆角）。",
      "body font-family 改为 typography.font_stack.sans；数值区域用 className=\"font-mono tabular-nums\"。",
      "移除 /app/frontend/src/App.css 中 .App-header 的居中布局影响（不要全局 text-align:center）。"
    ],
    "app_shell_build": [
      "实现 Sidebar + Header + Main 的三段式布局；Sidebar 桌面可折叠，移动端用 Sheet。",
      "Header 必须包含：全局搜索(Command)、更新时间、市场颜色惯例切换(CN/US)、深浅色切换(Switch)、用户菜单(DropdownMenu)。",
      "所有按钮/输入/表格行/关键数值都加 data-testid（kebab-case）。"
    ],
    "charts": [
      "Recharts 统一 Tooltip 样式：bg-card border-border text-foreground shadow-popover rounded-lg。",
      "线图：stroke 使用 data_viz_palette；网格线用 gridline（低对比）。",
      "涨跌色：按 market_color_rules 映射，不要硬编码红绿。"
    ],
    "tables": [
      "使用 shadcn Table + ScrollArea 实现横向滚动；表头 sticky。",
      "数值列右对齐 + font-mono tabular-nums；变化列加 up/down 颜色与小箭头（lucide-react）。",
      "行展开用 Drawer/Collapsible；原因解释默认 line-clamp-1。"
    ],
    "motion": [
      "避免全局 transition: all；仅对 button/input/badge hover 使用 transition-colors/opacity/shadow。",
      "数值变化可用短暂 highlight（CSS keyframes 120ms），尊重 prefers-reduced-motion。"
    ]
  },
  "appendix_general_ui_ux_design_guidelines": "<General UI UX Design Guidelines>  \n    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.\n</General UI UX Design Guidelines>"
}
