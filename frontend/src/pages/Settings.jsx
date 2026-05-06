import React, { useEffect, useState } from "react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { RadioGroup, RadioGroupItem } from "../components/ui/radio-group";
import { Input } from "../components/ui/input";
import { toast } from "sonner";
import api from "../lib/api";
import { Save } from "lucide-react";

const RISK_LABELS = {
  conservative: "保守",
  balanced: "平衡",
  medium_high: "中高 (默认)",
  high: "进取",
};

export default function Settings({ refreshTick, onRefreshDone }) {
  const [profile, setProfile] = useState("medium_high");
  const [thresholds, setThresholds] = useState(null);
  const [riskSig, setRiskSig] = useState({});
  const [fng, setFng] = useState({});

  useEffect(() => {
    api.riskProfile().then((r) => setProfile(r.risk_profile || "medium_high"));
    api.thresholds().then((t) => {
      setThresholds(t);
      setRiskSig(t.risk_signals || {});
      setFng(t.fng_thresholds || {});
    });
  }, [refreshTick]);

  const saveProfile = async () => {
    try {
      await api.setRiskProfile(profile);
      toast.success(`风险偏好已保存: ${RISK_LABELS[profile] || profile}`);
    } catch (e) { toast.error("保存失败"); }
  };
  const saveThresholds = async () => {
    try {
      const payload = { risk_signals: riskSig, fng_thresholds: fng };
      await api.updateThresholds(payload);
      toast.success("阈值已保存。\u4e0b\u6b21\u5237\u65b0\u6570\u636e\u540e\u751f\u6548\u3002");
    } catch (e) { toast.error("保存失败"); }
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">设置 · Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">风险偏好、策略阈值、报告调度</p>
      </div>

      <Card>
        <CardContent className="p-4 md:p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-wider text-muted-foreground">风险偏好 · Risk Profile</div>
              <div className="text-sm text-foreground mt-0.5">影响仓位上下限与推荐调性</div>
            </div>
            <Button size="sm" onClick={saveProfile} data-testid="save-risk-profile"><Save className="h-3.5 w-3.5 mr-1" /> 保存</Button>
          </div>
          <RadioGroup value={profile} onValueChange={setProfile} className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="settings-risk-profile">
            {Object.entries(RISK_LABELS).map(([k, lbl]) => (
              <Label key={k} htmlFor={`rp-${k}`} className="flex items-center gap-2 px-3 py-2 rounded-md border border-border cursor-pointer hover:bg-muted/40">
                <RadioGroupItem value={k} id={`rp-${k}`} />
                <span className="text-sm">{lbl}</span>
              </Label>
            ))}
          </RadioGroup>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4 md:p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="text-xs uppercase tracking-wider text-muted-foreground">F&G 阈值 · Phase Thresholds</div>
              <div className="text-sm text-muted-foreground">调整市场阶段划分</div>
            </div>
            <Button size="sm" onClick={saveThresholds} data-testid="save-thresholds"><Save className="h-3.5 w-3.5 mr-1" /> 保存</Button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3" data-testid="settings-strategy-thresholds">
            {["extreme_fear", "fear", "neutral", "greed", "extreme_greed"].map((k) => (
              <div key={k}>
                <Label className="text-xs text-muted-foreground">{k}</Label>
                <Input
                  type="number" value={fng[k] ?? ""}
                  onChange={(e) => setFng((p) => ({ ...p, [k]: parseFloat(e.target.value) || 0 }))}
                  className="h-9 mt-1"
                />
              </div>
            ))}
          </div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground mt-5 mb-2">风险信号阈值</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(riskSig).map(([k, v]) => (
              <div key={k}>
                <Label className="text-xs text-muted-foreground">{k}</Label>
                <Input
                  type="number" value={v}
                  onChange={(e) => setRiskSig((p) => ({ ...p, [k]: parseFloat(e.target.value) || 0 }))}
                  className="h-9 mt-1"
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4 md:p-5">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">调度 · Schedule</div>
          <div className="text-sm text-muted-foreground">
            每日自动刷新时间：北京时间 16:30 (A股收盘后)。可随时点顶部【刷新数据】手动刷新。
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
