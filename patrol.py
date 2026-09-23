import json
import datetime
import warnings

warnings.filterwarnings("ignore")
import akshare as ak

CODES = {
    "008163": "南方标普红利低波50A",
    "012761": "华泰柏瑞上证红利A",
    "017811": "东方人工智能主题混合C",
}

out = {"generated_at": datetime.datetime.now().isoformat(timespec="seconds"), "funds": [], "macro": {}}

for code, name in CODES.items():
    try:
        nav = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势").sort_values("净值日期")
        last, prev = nav.iloc[-1], nav.iloc[-2]
        wk = nav.iloc[-6] if len(nav) >= 6 else nav.iloc[0]
        info = ak.fund_individual_basic_info_xq(symbol=code)
        v = dict(zip(info["item"], info["value"]))
        out["funds"].append({
            "code": code,
            "name": name,
            "nav": float(last["单位净值"]),
            "nav_date": str(last["净值日期"]),
            "pct_1d": round((float(last["单位净值"]) / float(prev["单位净值"]) - 1) * 100, 2),
            "pct_1w": round((float(last["单位净值"]) / float(wk["单位净值"]) - 1) * 100, 2),
            "manager": str(v.get("基金经理")),
            "scale": str(v.get("最新规模")),
        })
    except Exception as e:
        out["funds"].append({"code": code, "name": name, "error": str(e)[:120]})

try:
    pe = ak.stock_index_pe_lg(symbol="沪深300")
    out["macro"]["hs300_pe_ttm"] = float(pe["滚动市盈率"].iloc[-1])
    out["macro"]["hs300_pe_date"] = str(pe["日期"].iloc[-1])
except Exception as e:
    out["macro"]["hs300_error"] = str(e)[:120]

try:
    bond = ak.bond_zh_us_rate()
    bond = bond.dropna(subset=["中国国债收益率10年"])
    out["macro"]["cn10y"] = float(bond["中国国债收益率10年"].iloc[-1])
    out["macro"]["cn10y_date"] = str(bond["日期"].iloc[-1])
except Exception as e:
    out["macro"]["bond_error"] = str(e)[:120]

with open("latest.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

today = datetime.date.today().isoformat()
with open(f"history/{today}.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(json.dumps(out, ensure_ascii=False, indent=2))
