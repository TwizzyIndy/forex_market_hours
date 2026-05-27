#!/usr/bin/env python3

import os
import argparse

# ─────────────────────────────────────────────
# ANSI colors
# ─────────────────────────────────────────────
R    = "\033[91m"
G    = "\033[92m"
Y    = "\033[93m"
M    = "\033[95m"
C    = "\033[96m"
W    = "\033[97m"
DIM  = "\033[2m"
BOLD = "\033[1m"
RST  = "\033[0m"

def clr(text, color): return f"{color}{text}{RST}"
def bold(text):        return f"{BOLD}{text}{RST}"
def dim(text):         return f"{DIM}{text}{RST}"

# ─────────────────────────────────────────────
# Table helper
# ─────────────────────────────────────────────
def print_table(headers, rows, col_colors=None, title=None):
    all_rows = [headers] + rows
    widths = [max(len(str(cell)) for cell in col) for col in zip(*all_rows)]
    sep = "┼".join("─" * (w + 2) for w in widths)
    top = "┬".join("─" * (w + 2) for w in widths)
    bot = "┴".join("─" * (w + 2) for w in widths)
    total_width = sum(w + 3 for w in widths) + 1

    if title:
        print(f"┌{'─' * (total_width - 2)}┐")
        print(f"│{bold(title.center(total_width - 2))}│")
        print(f"├{top}┤")
    else:
        print(f"┌{top}┐")

    header_cells = [f" {bold(clr(str(h), C))}{' ' * (w - len(str(h)))} "
                    for h, w in zip(headers, widths)]
    print("│" + "│".join(header_cells) + "│")
    print(f"├{sep}┤")

    for r_idx, row in enumerate(rows):
        cells = []
        for i, (cell, w) in enumerate(zip(row, widths)):
            raw = str(cell)
            color = col_colors[i] if col_colors else W
            if callable(color):
                color = color(raw, r_idx)
            cells.append(f" {clr(raw, color)}{' ' * (w - len(raw))} ")
        print("│" + "│".join(cells) + "│")

    print(f"└{bot}┘")

def section(title):
    print()
    print(clr(f"  ◈  {title}", M))
    print(clr("  " + "─" * (len(title) + 5), DIM))

# ─────────────────────────────────────────────
# Input helpers
# ─────────────────────────────────────────────
def get_float_input(prompt_text, min_value=0.0, max_value=None):
    """Prompt for a float with validation. Matches your existing style."""
    while True:
        try:
            value = float(input(prompt_text))
            if value < min_value or (max_value is not None and value > max_value):
                limit = f">= {min_value}"
                if max_value is not None:
                    limit += f" and <= {max_value}"
                print(f"  Value must be {limit}")
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a number.")
        except EOFError:
            return min_value

def get_int_input(prompt_text, min_value=1, max_value=None):
    while True:
        try:
            value = int(input(prompt_text))
            if value < min_value or (max_value is not None and value > max_value):
                print(f"  Value must be >= {min_value}" + (f" and <= {max_value}" if max_value else ""))
                continue
            return value
        except ValueError:
            print("  Invalid input. Please enter a whole number.")
        except EOFError:
            return min_value

def get_str_input(prompt_text, default="SPOT"):
    try:
        val = input(prompt_text).strip()
        return val if val else default
    except EOFError:
        return default

# ─────────────────────────────────────────────
# Core calculations
# ─────────────────────────────────────────────
TRADING_DAYS_PER_MONTH = 20
MONTHS_PER_YEAR        = 12
TRADING_DAYS_PER_WEEK  = 5


def calculate_risk_and_profit(capital, daily_profit_pct, daily_risk_pct, position_size_pct):
    """
    Calculate all risk/profit metrics from capital and percentages only.
    No entry or stop price needed.
    """
    position_size       = (capital * position_size_pct) / 100
    max_risk_per_trade  = (capital * daily_risk_pct) / 100
    risk_pct_on_pos     = (max_risk_per_trade / position_size * 100) if position_size else 0

    min_daily_profit    = (position_size * daily_profit_pct) / 100
    max_daily_profit    = (capital       * daily_profit_pct) / 100
    min_daily_loss      = (position_size * daily_risk_pct)   / 100
    max_daily_loss      = (capital       * daily_risk_pct)   / 100

    td_month = TRADING_DAYS_PER_MONTH
    months   = MONTHS_PER_YEAR

    return {
        "position_size":        position_size,
        "max_risk_per_trade":   max_risk_per_trade,
        "risk_pct_on_pos":      risk_pct_on_pos,

        "min_daily_profit":     min_daily_profit,
        "max_daily_profit":     max_daily_profit,
        "min_daily_loss":       min_daily_loss,
        "max_daily_loss":       max_daily_loss,

        "min_weekly_profit":    min_daily_profit  * TRADING_DAYS_PER_WEEK,
        "max_weekly_profit":    max_daily_profit  * TRADING_DAYS_PER_WEEK,
        "min_weekly_loss":      min_daily_loss    * TRADING_DAYS_PER_WEEK,
        "max_weekly_loss":      max_daily_loss    * TRADING_DAYS_PER_WEEK,

        "min_monthly_profit":   min_daily_profit  * td_month,
        "max_monthly_profit":   max_daily_profit  * td_month,
        "min_monthly_loss":     min_daily_loss    * td_month,
        "max_monthly_loss":     max_daily_loss    * td_month,

        "min_yearly_profit":    min_daily_profit  * td_month * months,
        "max_yearly_profit":    max_daily_profit  * td_month * months,
        "min_yearly_loss":      min_daily_loss    * td_month * months,
        "max_yearly_loss":      max_daily_loss    * td_month * months,
    }


def calculate_drawdown_limits(capital, dd_day_pct, dd_month_pct, dd_year_pct, risk_per_trade):
    """Max USD loss per period and how many losing trades it takes to hit each limit."""
    dd_day   = capital * dd_day_pct   / 100
    dd_month = capital * dd_month_pct / 100
    dd_year  = capital * dd_year_pct  / 100
    trades   = lambda usd: int(usd // risk_per_trade) if risk_per_trade else 0
    return {
        "dd_day_usd":   dd_day,
        "dd_month_usd": dd_month,
        "dd_year_usd":  dd_year,
        "trades_day":   trades(dd_day),
        "trades_month": trades(dd_month),
        "trades_year":  trades(dd_year),
    }


def calculate_required_capital(expected_daily_profit, daily_profit_pct, position_size_pct):
    """
    Required capital so that position_size_pct of it, grown by daily_profit_pct,
    equals expected_daily_profit.
    """
    if daily_profit_pct > 0 and position_size_pct > 0:
        return expected_daily_profit / ((position_size_pct / 100) * (daily_profit_pct / 100))
    return None


def calculate_trade_stats(win_rate, avg_win_pct, avg_loss_pct):
    """Kelly, expectancy, profit factor."""
    p = win_rate / 100
    q = 1 - p
    kelly = 0.0
    if avg_loss_pct > 0:
        b = avg_win_pct / avg_loss_pct
        kelly = max((b * p - q) / b, 0)
    expectancy   = (p * avg_win_pct) - (q * avg_loss_pct)
    profit_factor = (p * avg_win_pct) / (q * avg_loss_pct) if (q * avg_loss_pct) > 0 else float("inf")
    be_win_rate   = avg_loss_pct / (avg_win_pct + avg_loss_pct) * 100 if (avg_win_pct + avg_loss_pct) > 0 else 0
    return {
        "expectancy":    expectancy,
        "kelly_full":    kelly * 100,
        "kelly_quarter": kelly * 25,
        "profit_factor": profit_factor,
        "rr_ratio":      avg_win_pct / avg_loss_pct if avg_loss_pct > 0 else 0,
        "be_win_rate":   be_win_rate,
    }


def calculate_consecutive_loss_survival(capital, risk_per_trade_pct):
    """Account value after N consecutive losses."""
    r = risk_per_trade_pct / 100
    rows = []
    for n in [5, 10, 15, 20]:
        remaining = capital * (1 - r) ** n
        rows.append((n, remaining, (1 - r) ** n * 100))
    # trades to wipe 50 / 75 / 90 %
    blow = {}
    for threshold in [50, 75, 90]:
        val, n = 100.0, 0
        while val > (100 - threshold) and n < 100000:
            val *= (1 - r)
            n += 1
        blow[threshold] = n
    return rows, blow


def calculate_drawdown_recovery():
    """Static table: drawdown % → recovery % needed."""
    rows = []
    for dd in [5, 10, 15, 20, 25, 30, 40, 50, 60, 75]:
        rec  = (dd / (100 - dd)) * 100 if dd < 100 else float("inf")
        flag = "⛔" if dd >= 50 else ("⚠" if dd >= 25 else "")
        rows.append((dd, rec, flag))
    return rows


# ─────────────────────────────────────────────
# Display helpers
# ─────────────────────────────────────────────
def fmt_range(lo, hi):
    return f"${lo:,.2f}  ~  ${hi:,.2f}"

def print_header(symbol):
    print()
    print(clr("╔══════════════════════════════════════════════════════╗", C))
    print(clr("║   SPOT TRADING RISK MANAGEMENT CALCULATOR  v2.0      ║", C))
    print(clr("╚══════════════════════════════════════════════════════╝", C))
    if symbol:
        print(f"  {dim('Symbol:')} {clr(symbol, Y)}")


# ─────────────────────────────────────────────
# Option 1 — full risk/profit report
# ─────────────────────────────────────────────
def run_option1(args):
    print()
    print(clr("  ── Option 1: Risk & Profit Report ──", C))
    print()

    if args.capital is not None:
        capital = args.capital
        print(f"  Trading capital             : {capital}")
    else:
        capital = get_float_input("  Trading capital ($)         : ", min_value=0.01)

    if args.profit_pct is not None:
        daily_profit_pct = args.profit_pct
        print(f"  Daily profit target (%%)     : {daily_profit_pct}")
    else:
        daily_profit_pct = get_float_input("  Daily profit target (%%)     : ", min_value=0.01, max_value=100)

    if args.risk_pct is not None:
        daily_risk_pct = args.risk_pct
        print(f"  Daily risk (%%)              : {daily_risk_pct}")
    else:
        daily_risk_pct = get_float_input("  Daily risk (%%)              : ", min_value=0.01, max_value=100)

    if args.pos_size is not None:
        position_size_pct = args.pos_size
        print(f"  Position size per trade (%%) : {position_size_pct}")
    else:
        position_size_pct = get_float_input("  Position size per trade (%%) : ", min_value=0.01, max_value=100)

    # Drawdown limits
    print()
    if args.dd_day is not None:
        dd_day_pct = args.dd_day
    else:
        dd_day_pct   = get_float_input("  Max drawdown / day (%%)      : ", min_value=0.01, max_value=100)

    if args.dd_month is not None:
        dd_month_pct = args.dd_month
    else:
        dd_month_pct = get_float_input("  Max drawdown / month (%%)    : ", min_value=0.01, max_value=100)

    if args.dd_year is not None:
        dd_year_pct = args.dd_year
    else:
        dd_year_pct  = get_float_input("  Max drawdown / year (%%)     : ", min_value=0.01, max_value=100)

    # Win stats
    print()
    if args.win_rate is not None:
        win_rate = args.win_rate
    else:
        win_rate     = get_float_input("  Historical win rate (%%)     : ", min_value=0.01, max_value=100)

    if args.avg_win is not None:
        avg_win_pct = args.avg_win
    else:
        avg_win_pct  = get_float_input("  Average win per trade (%%)   : ", min_value=0.01)

    if args.avg_loss is not None:
        avg_loss_pct = args.avg_loss
    else:
        avg_loss_pct = get_float_input("  Average loss per trade (%%)  : ", min_value=0.01)

    # ── Calculate ─────────────────────────────
    r   = calculate_risk_and_profit(capital, daily_profit_pct, daily_risk_pct, position_size_pct)
    dd  = calculate_drawdown_limits(capital, dd_day_pct, dd_month_pct, dd_year_pct, r["max_risk_per_trade"])
    ts  = calculate_trade_stats(win_rate, avg_win_pct, avg_loss_pct)
    cl_rows, blow = calculate_consecutive_loss_survival(capital, daily_risk_pct)
    dr_rows = calculate_drawdown_recovery()

    symbol = args.symbol or ""
    os.system("clear" if os.name == "posix" else "cls")
    print_header(symbol)

    # 1. Position & Risk
    section("1. POSITION & RISK PER TRADE")
    print_table(
        ["Parameter", "Value"],
        [
            ["Trading Capital",          f"${capital:,.2f}"],
            ["Position Size / Trade",    f"${r['position_size']:,.2f}  ({position_size_pct:.2f}% of capital)"],
            ["Max Risk / Trade (USD)",   f"${r['max_risk_per_trade']:,.2f}  ({daily_risk_pct:.2f}% of capital)"],
            ["Risk % on Position",       f"{r['risk_pct_on_pos']:.2f}%"],
        ],
        col_colors=[Y, W], title="Position & Risk"
    )

    # 2. Drawdown Limits
    section("2. DRAWDOWN LIMITS")
    print_table(
        ["Period", "Max DD %", "Max Loss (USD)", "Max Losing Trades"],
        [
            ["Per Trade", f"{daily_risk_pct:.2f}%",  f"${r['max_risk_per_trade']:,.2f}", "1"],
            ["Per Day",   f"{dd_day_pct:.2f}%",      f"${dd['dd_day_usd']:,.2f}",        str(dd['trades_day'])],
            ["Per Month", f"{dd_month_pct:.2f}%",    f"${dd['dd_month_usd']:,.2f}",      str(dd['trades_month'])],
            ["Per Year",  f"{dd_year_pct:.2f}%",     f"${dd['dd_year_usd']:,.2f}",       str(dd['trades_year'])],
        ],
        col_colors=[Y, R, R, W], title="Drawdown Limits"
    )

    # 3. Profit / Loss Range
    section("3. PROFIT & LOSS RANGE  (position size ↔ full capital)")
    print_table(
        ["Period", "Profit Range (USD)", "Loss Range (USD)"],
        [
            ["Daily",   fmt_range(r["min_daily_profit"],   r["max_daily_profit"]),
                        fmt_range(r["min_daily_loss"],     r["max_daily_loss"])],
            ["Weekly",  fmt_range(r["min_weekly_profit"],  r["max_weekly_profit"]),
                        fmt_range(r["min_weekly_loss"],    r["max_weekly_loss"])],
            ["Monthly", fmt_range(r["min_monthly_profit"], r["max_monthly_profit"]),
                        fmt_range(r["min_monthly_loss"],   r["max_monthly_loss"])],
            ["Yearly",  fmt_range(r["min_yearly_profit"],  r["max_yearly_profit"]),
                        fmt_range(r["min_yearly_loss"],    r["max_yearly_loss"])],
        ],
        col_colors=[Y, G, R], title="Profit & Loss Projection"
    )

    # 4. Drawdown Recovery
    section("4. DRAWDOWN RECOVERY COST")
    print_table(
        ["Drawdown", "Recovery Needed", ""],
        [[f"{d}%", f"{rec:.2f}%", flag] for d, rec, flag in dr_rows],
        col_colors=[R, Y, W], title="Recovery from Drawdown"
    )

    # 5. Trade Statistics
    section("5. EDGE & TRADE STATISTICS")
    pf_str = f"{ts['profit_factor']:.2f}x" if ts['profit_factor'] != float("inf") else "∞"
    print_table(
        ["Metric", "Value", "Note"],
        [
            ["Win Rate",           f"{win_rate:.1f}%",         "Historical win %"],
            ["Avg Win",            f"{avg_win_pct:.2f}%",      "Per winning trade"],
            ["Avg Loss",           f"{avg_loss_pct:.2f}%",     "Per losing trade"],
            ["Reward : Risk",      f"{ts['rr_ratio']:.2f}x",   ">1.5 preferred"],
            ["Expectancy",         f"{ts['expectancy']:.4f}%", "Per trade edge (>0 = edge)"],
            ["Full Kelly %",       f"{ts['kelly_full']:.2f}%", "Theoretical max risk"],
            ["Quarter Kelly %",    f"{ts['kelly_quarter']:.2f}%","Recommended safe risk"],
            ["Profit Factor",      pf_str,                     ">1.5 is solid"],
            ["Break-even Win %",   f"{ts['be_win_rate']:.1f}%","Min win rate to not lose money"],
        ],
        col_colors=[Y, W, DIM], title="Trade Statistics & Edge"
    )

    # 6. Consecutive Loss Survival
    section("6. CONSECUTIVE LOSS SURVIVAL")
    surv_rows = [
        [f"{n} losses", f"${acc:,.2f}", f"{pct:.1f}% remaining"]
        for n, acc, pct in cl_rows
    ] + [
        [f"50% wiped",  f"${capital*0.50:,.2f}", f"{blow[50]} consecutive losses"],
        [f"75% wiped",  f"${capital*0.25:,.2f}", f"{blow[75]} consecutive losses"],
        [f"90% wiped",  f"${capital*0.10:,.2f}", f"{blow[90]} consecutive losses"],
    ]
    print_table(
        ["Scenario", "Account Left", "Note"],
        surv_rows,
        col_colors=[Y, W, DIM], title=f"Survival at {daily_risk_pct}% Risk Per Trade"
    )

    # Footer
    print()
    print(clr("  ─────────────────────────────────────────────────────", DIM))
    print(f"  {clr('REMINDER:', Y)} Spot = no forced liquidation, but capital is still at risk.")
    dd_limit_usd = f"${dd['dd_day_usd']:,.2f}"
    dd_limit_trades = str(dd['trades_day'])
    print(f"  {clr('DAILY LIMIT:', Y)} Stop trading after {clr(dd_limit_usd, R)} loss ({clr(dd_limit_trades, R)} full-risk trades)")
    print(clr("  ─────────────────────────────────────────────────────", DIM))
    print()


# ─────────────────────────────────────────────
# Option 2 — required capital
# ─────────────────────────────────────────────
def run_option2(args):
    print()
    print(clr("  ── Option 2: Required Capital Calculator ──", C))
    print()

    if args.target_profit is not None:
        expected_profit = args.target_profit
        print(f"  Expected daily profit ($)   : {expected_profit}")
    else:
        expected_profit  = get_float_input("  Expected daily profit ($)   : ", min_value=0.01)

    if args.profit_pct is not None:
        daily_profit_pct = args.profit_pct
        print(f"  Daily profit target (%%)     : {daily_profit_pct}")
    else:
        daily_profit_pct = get_float_input("  Daily profit target (%%)     : ", min_value=0.01, max_value=100)

    if args.pos_size is not None:
        position_size_pct = args.pos_size
        print(f"  Position size per trade (%%) : {position_size_pct}")
    else:
        position_size_pct = get_float_input("  Position size per trade (%%) : ", min_value=0.01, max_value=100)

    required = calculate_required_capital(expected_profit, daily_profit_pct, position_size_pct)

    os.system("clear" if os.name == "posix" else "cls")
    print_header(args.symbol or "")
    section("REQUIRED CAPITAL CALCULATOR")

    if required is not None:
        monthly = expected_profit * TRADING_DAYS_PER_MONTH
        yearly  = monthly * MONTHS_PER_YEAR
        print_table(
            ["Metric", "Value"],
            [
                ["Daily profit target",     f"${expected_profit:,.2f}"],
                ["Daily profit target %",   f"{daily_profit_pct:.2f}%  of position"],
                ["Position size %",         f"{position_size_pct:.2f}%  of capital"],
                ["Required Capital",        f"${required:,.2f}"],
                ["Monthly profit (linear)", f"${monthly:,.2f}"],
                ["Yearly profit (linear)",  f"${yearly:,.2f}"],
            ],
            col_colors=[Y, W], title="Required Capital"
        )
        print()
        print(f"  {clr('▸', Y)} You need at least {clr(f'${required:,.2f}', G)} to earn "
              f"{clr(f'${expected_profit:,.2f}/day', G)} at "
              f"{daily_profit_pct:.2f}% on a {position_size_pct:.2f}% position.")
    else:
        print(clr("  Cannot calculate — check that profit % and position size % are > 0.", R))
    print()


# ─────────────────────────────────────────────
# Argparser
# ─────────────────────────────────────────────
def build_parser():
    p = argparse.ArgumentParser(
        prog="risk_calc",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
  ╔══════════════════════════════════════════════════════╗
  ║   SPOT TRADING RISK MANAGEMENT CALCULATOR  v2.0      ║
  ║                   by TwizzyIndy                      ║
  ╚══════════════════════════════════════════════════════╝

  Two modes (choose with --mode or via interactive menu):

    Mode 1  Risk & Profit Report
            --mode 1 --capital 10000 --profit-pct 1.5 --risk-pct 1 --pos-size 20
                     --dd-day 3 --dd-month 10 --dd-year 25
                     --win-rate 55 --avg-win 2.5 --avg-loss 1.2

    Mode 2  Required Capital Calculator
            --mode 2 --target-profit 150 --profit-pct 1.5 --pos-size 20

  Any omitted flag will be prompted interactively.
""",
    )

    p.add_argument("--mode", type=int, choices=[1, 2], metavar="N",
                   help="1 = Risk/Profit report  |  2 = Required capital")
    p.add_argument("--symbol", type=str, metavar="PAIR", default=None,
                   help="Trading pair label  (e.g. BTC/USDT)")
    p.add_argument("--no-color", action="store_true",
                   help="Disable ANSI color output")

    g1 = p.add_argument_group("Mode 1 — Risk & Profit")
    g1.add_argument("--capital",     type=float, metavar="USD",  help="Trading capital in USD")
    g1.add_argument("--profit-pct",  type=float, metavar="PCT",  help="Daily profit target %%")
    g1.add_argument("--risk-pct",    type=float, metavar="PCT",  help="Daily risk %%")
    g1.add_argument("--pos-size",    type=float, metavar="PCT",  help="Position size per trade %%")
    g1.add_argument("--dd-day",      type=float, metavar="PCT",  help="Max drawdown / day %%")
    g1.add_argument("--dd-month",    type=float, metavar="PCT",  help="Max drawdown / month %%")
    g1.add_argument("--dd-year",     type=float, metavar="PCT",  help="Max drawdown / year %%")
    g1.add_argument("--win-rate",    type=float, metavar="PCT",  help="Historical win rate %%")
    g1.add_argument("--avg-win",     type=float, metavar="PCT",  help="Average win per trade %%")
    g1.add_argument("--avg-loss",    type=float, metavar="PCT",  help="Average loss per trade %%")

    g2 = p.add_argument_group("Mode 2 — Required Capital")
    g2.add_argument("--target-profit", type=float, metavar="USD", help="Expected daily profit ($)")

    return p


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    parser = build_parser()
    args   = parser.parse_args()

    if args.no_color:
        global R, G, Y, M, C, W, DIM, BOLD, RST
        R = G = Y = M = C = W = DIM = BOLD = RST = ""

    os.system("clear" if os.name == "posix" else "cls")
    print()
    print(clr("╔══════════════════════════════════════════════════════╗", C))
    print(clr("║   SPOT TRADING RISK MANAGEMENT CALCULATOR  v2.0      ║", C))
    print(clr("║                   by TwizzyIndy                      ║", DIM))
    print(clr("╚══════════════════════════════════════════════════════╝", C))
    print()

    # Resolve mode
    if args.mode is not None:
        choice = str(args.mode)
    else:
        print(clr("  1.", Y) + "  Risk & Profit Report")
        print(clr("  2.", Y) + "  Required Capital Calculator")
        print()
        choice = input("  Choose an option (1 or 2): ").strip()
        print()

    if choice == "1":
        run_option1(args)
    elif choice == "2":
        run_option2(args)
    else:
        print(clr("  Invalid option. Run again and choose 1 or 2.", R))


if __name__ == "__main__":
    main()
