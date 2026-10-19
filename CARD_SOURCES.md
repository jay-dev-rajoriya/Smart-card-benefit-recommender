# Card sources and modelling notes

Catalog last reviewed: **16 October 2026**.

The application uses issuer-published pages or terms. Merchant category codes, posting dates, reversals, taxes, and bank-side classification can change the actual credit. A displayed reward is therefore an estimate, not a promise.

| Card | Primary source | Modelled headline rules |
|---|---|---|
| CASHBACK SBI Card | [SBI Card revised benefits](https://www.sbicard.com/cashback-revised) | 5% online and 1% offline; separate ₹2,000 statement-cycle caps; issuer exclusions applied. |
| Amazon Pay ICICI | [ICICI FAQ](https://www.icicibank.com/personal-banking/cards/credit-card/amazon-pay-credit-card/amazon-pay-faq) | 5% Prime / 3% non-Prime on Amazon; 2% partners; 1% eligible base spend. |
| HDFC Millennia | [HDFC product page](https://www.hdfc.bank.in/credit-cards/millennia-credit-card) | 5% select merchants and 1% base, each with ₹1,000 cycle cap. |
| Swiggy HDFC | [HDFC product page](https://www.hdfc.bank.in/credit-cards/swiggy-hdfc-bank-credit-card) | 10% Swiggy, 5% eligible online categories, 1% base with separate caps. |
| Flipkart Axis | [Axis product page](https://www.axisbank.com/retail/cards/credit-card/flipkart-axisbank-credit-card/features-benefits) | 7.5% Myntra, 5% Flipkart/Cleartrip and 1% base; quarterly partner caps modelled. |
| Airtel Axis | [Axis cashback terms](https://www.axisbank.com/docs/default-source/default-document-library/credit-cards/terms-and-conditions-for-cashback-for-airtel-axis-bank-credit-card.pdf/1000) | 25% Airtel, 10% utilities and preferred food merchants through qualifying apps, plus 1% base. |
| HSBC Live+ | [HSBC product page](https://www.hsbc.co.in/credit-cards/products/live-plus/) | 10% dining/grocery/food delivery capped at ₹1,000 monthly; 1.5% eligible base spend. |
| Axis Cashback | [Axis terms](https://www.axisbank.com/docs/default-source/ld/axis-bank-cashback-credit-card-tnc.pdf) | Up to 7% eligible online spend and 0.75% offline/travel. The UI labels 7% as a tier maximum. |

## Assumptions

- The evaluator uses entered merchant, channel, membership and exclusion tags as proxies for issuer MCC and merchant-ID classification.
- Cap usage can be supplied to the engine. The current UI estimates a single purchase and does not reconstruct every issuer statement cycle.
- Fee waivers are applied in the annual calculator when annual modelled spend reaches the published threshold.
- GST on fees, welcome offers, lounge access, instant discounts, reward redemption friction and interest are excluded from reward rankings.
