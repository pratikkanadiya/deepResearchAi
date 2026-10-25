# Artificial Intelligence in Precision Agriculture: Evidence, Economics, Sustainability and Governance

**Evidence synthesis | 24 October 2026**

## Executive summary

Artificial intelligence (AI) is useful in agriculture when it improves a concrete decision—where to scout, when to irrigate, how much nutrient to apply, or which animal needs attention—and when a farmer can act on its recommendation. Machine learning (ML), deep learning and computer vision now support crop and livestock monitoring, disease and weed detection, yield estimation, irrigation scheduling, breeding, logistics and advisory services. These tools augment sensors, satellite imagery, machinery and agronomic expertise; they do not create reliable recommendations from data alone.

Benefits are real but uneven. A 2025 meta-analysis of 85 studies and 1,472 farm observations estimated average precision-agriculture gains of 22.3% in ROI and 18.5% in net profit, alongside 15.1% better nitrogen-use efficiency, 12.8% lower pesticide application and 9.4% lower greenhouse-gas emissions. The authors also reported substantial heterogeneity (ROI I²=82.1%), so these pooled estimates should not be promised to an individual farm (Lan & Ban, 2025). In an Arkansas three-year soybean trial, See & Spray reduced post-emergence herbicide use 43–59%; a low-sensitivity treatment produced about four bushels/acre more soybean but also more Palmer amaranth, illustrating that operating settings involve agronomic trade-offs (University of Arkansas System Division of Agriculture, 2025).

Large, capitalized farms in North America and Europe are best positioned to capture returns from costly machinery and data systems. Smallholders can benefit through shared services, mobile advice, cooperatives and locally adapted low-bandwidth tools, but often face device, connectivity, finance, skills and trust barriers. The evidence base remains stronger for input use and machine performance than for long-term soil carbon, biodiversity, whole-farm profitability or equitable distribution. The sensible policy priority is therefore measurable, farmer-controlled and locally validated AI, supported by extension services, interoperable data systems and clear rules on data use.

## Introduction and scope

Precision agriculture (PA) uses spatial and temporal data to manage within-field or animal-level variation. AI here means statistical learning and computational perception used to classify, predict, optimize or generate advice. This report covers crop monitoring, livestock, soil, pests, supply chains, breeding, economics, sustainability, adoption barriers, law and policy. It distinguishes peer-reviewed research and independent field evidence from vendor claims. Evidence priorities are 2018–2026, with older foundational work included where useful. This is a focused narrative synthesis, not a registered systematic review; quantitative estimates are reported with their original context and should not be treated as universal causal effects.

## Methodology

The evidence review used targeted searches of peer-reviewed and official sources for AI/ML in agriculture, precision-agriculture impacts and adoption, field trials, policy and data protection. Sources were included when they provided (a) a review or empirical study with an identifiable method, (b) primary field evidence, or (c) an official legal or policy description. Vendor material was used only to describe products or company-reported deployment, and is identified as such. Priority was given to papers with DOI, university field studies, FAO/World Bank publications, and government legislation or program pages. Study designs differ greatly; a technology trial in a row-crop field is not equivalent to an adoption survey or a modeled environmental estimate. Reported effect sizes are therefore kept attached to the specific source and context.

## Findings

### 1. AI methods by agricultural sub-domain

| Sub-domain | Common AI methods and inputs | Representative decisions |
|---|---|---|
| Crop monitoring and yield | Random forests, gradient boosting, CNNs, time-series/deep learning; satellite/UAV imagery, weather, soil and machinery data | Estimate crop stage, biomass, stress, yield and harvest timing (Benos et al., 2021; Ben Ayed & Hanana, 2021) |
| Livestock | Computer vision, acoustic ML, anomaly detection, Bayesian models; cameras, microphones, wearables and milking sensors | Detect lameness, illness, estrus, feeding changes and welfare risks (Benos et al., 2021) |
| Soil and nutrient management | Regression/ensemble ML, geospatial models and sensor fusion; soil samples, proximal sensors, imagery | Map nutrients and moisture, forecast nutrient demand, guide variable-rate application |
| Pest, disease and weeds | CNNs/vision transformers, object detection, segmentation and classification; leaf images and field cameras | Identify disease symptoms or weeds; target scouting and spraying |
| Irrigation | Forecasting, reinforcement learning/control, optimization and evapotranspiration models; weather and soil-moisture sensors | Schedule irrigation subject to crop stage, water limits and energy cost |
| Supply chain and markets | Time-series forecasting, graph/route optimization, NLP and anomaly detection | Forecast demand, reduce spoilage, plan storage/transport and monitor traceability |
| Breeding and phenotyping | Genomic prediction, computer vision, Bayesian/ensemble models and NLP over research records | Rank breeding lines, automate trait measurement and prioritize crosses |

Method choice depends on the decision and data. Image models can perform well on curated datasets but fail under new lighting, varieties, backgrounds or disease prevalence. Reviews emphasize that external validation, representative labels and farm-level deployment matter at least as much as benchmark accuracy (Benos et al., 2021; Ben Ayed & Hanana, 2021).

### 2. Precision-farming benefits and observed field outcomes

The often-repeated headline that AI routinely saves 15–30% water or fertilizer should be treated cautiously: effects vary with baseline practice, weather, crop, soil, equipment, and whether AI itself or the broader PA package caused the change. A recent meta-analysis found average 15.1% higher nitrogen-use efficiency and 12.8% lower pesticide application across pooled PA studies, but it did not establish those as guaranteed AI-only effects (Lan & Ban, 2025). The 2026 systematic review of environmental PA evidence found 54 field-trial studies among 444 publications screened; 45 reported at least one environmental benefit, while 9 field trials did not. Benefits were most frequently reduced fertilizer use, and the authors noted geographic and crop concentration in the evidence base (Ruder et al., 2026).

See & Spray illustrates a measurable application. The University of Arkansas’ three-year soybean trial reported 43–59% lower post-emergence herbicide use compared with broadcast application. At the low-sensitivity setting, researchers observed approximately four bushels/acre more soybean but a significant increase in Palmer amaranth. The result is specific to the crop, trial conditions, setting and weed pressure; it supports targeted application as a tool, not the claim that herbicide can always be cut in half without consequences (University of Arkansas System Division of Agriculture, 2025). John Deere separately reported an average 59% herbicide savings over more than one million acres in 2024. This is a company-reported deployment figure and should be interpreted in light of selection, measurement and marketing incentives (John Deere, 2024).

### 3. Economics and ROI by farm size and region

Lan and Ban’s 2025 global meta-analysis synthesized 85 empirical studies and 1,472 independent farm observations. It estimated average ROI 22.3% higher (58 studies; p<.001), net profit 18.5% higher (63 studies; p<.001), nitrogen-use efficiency 15.1% higher, pesticide application 12.8% lower and GHG emissions 9.4% lower. High heterogeneity was reported for ROI (I²=82.1%), profit (79.5%) and nitrogen efficiency (76.8%). The estimates aggregate precision technologies, not AI alone, and the study’s inclusion and conversion assumptions should be consulted before using them in investment models (Lan & Ban, 2025).

| Farm/region | Economic pattern in the evidence | Practical interpretation |
|---|---|---|
| Medium/large farms, North America and Europe | Higher ability to amortize guidance, variable-rate hardware, cloud subscriptions and skilled operators; strongest evidence for row crops and machinery-based PA | ROI is most plausible where acreage is large, input costs high, equipment interoperable and labor scarce. Capex, subscription and repair costs still matter. |
| Small farms, Europe/Asia-Pacific | Outcomes depend on crop value, fragmentation, service availability and cooperative access | Per-acre machinery purchases may not pay; pay-per-use scouting, shared equipment and mobile decision support can reduce entry cost. |
| Smallholders, Africa and Latin America | Lower device access, connectivity, finance and localized data constrain deployment; evidence often comes from pilots rather than long-run farm accounts | Evaluate net benefit after fees, data costs, farmer time and downside risk. Aggregated advisory and extension channels may be more viable than autonomous machinery. |
| Asia-Pacific, mixed farm structures | Wide variation from highly mechanized operations to tiny plots; no defensible single regional ROI | Local crop mix, land tenure, irrigation access and labor costs dominate averages. |

OECD’s review similarly identifies upfront and recurring costs, limited use cases, skills requirements, usability, mistrust and technological risk as barriers in digitally enabled farming (OECD, 2022). These findings argue against applying one ROI estimate across farm types. A credible business case should measure a local baseline, compare whole-season costs and benefits, and include bad-year performance and switching costs.

### 4. Environmental sustainability

AI-enabled targeting can reduce surplus fertilizer, pesticide, water, fuel or feed when the model’s recommendation is accurate and equipment can deliver it. The PA meta-analysis estimates 9.4% lower GHG emissions, primarily associated with more efficient nitrogen and operations, while the 2026 systematic review found field evidence of fertilizer, chemical, water/runoff, soil-quality and fuel benefits across a subset of studies (Lan & Ban, 2025; Ruder et al., 2026). These findings support potential, not a blanket lifecycle claim: rebound effects, extra sensors/equipment, energy use, land-use change, and shifts in production can offset some gains.

Evidence on soil organic carbon and biodiversity is especially limited and slow-moving. Reduced chemical use can lower exposure pathways, but biodiversity outcomes depend on landscape, chemical toxicity, application timing and non-target effects. Carbon changes require multi-year sampling and consistent baselines. Governments and vendors should report measured outcomes and uncertainty rather than proxying sustainability with model accuracy or input savings alone.

### 5. Barriers and mitigation

Technical barriers include missing and noisy sensor data, weak labels, model drift across seasons and geographies, limited interoperability, latency/connectivity, cybersecurity and poor explanations for recommendations. Nontechnical barriers include equipment and subscription cost, limited credit, digital skills, language access, unequal bargaining power, uncertain ownership, and low trust. FAO’s ten case studies across sub-Saharan Africa, Latin America/Caribbean and Asia found that small-scale solutions were often smartphone/tablet-based and that investment cost, digital skills and an enabling environment were major adoption constraints (McCampbell, 2022). The World Bank likewise highlights connectivity, electricity, cost, local data and digital literacy as barriers to smallholder AI (World Bank, 2025).

Mitigations with practical grounding include farmer cooperatives and machinery-as-a-service; public extension agents who validate recommendations and receive feedback; offline or voice interfaces in local languages; open standards and portable farm records; local participatory data collection; and staged pilots with independent agronomic evaluation. Human review is essential when a wrong diagnosis could destroy a crop or trigger unsafe chemical use. Models should communicate confidence and abstain when inputs are out of distribution.

### 6. Privacy, ownership and ethics

Farm data may identify an individual or household, reveal business-sensitive yields and costs, or expose land and resource use. GDPR applies to personal data within its scope and requires a lawful basis, transparency, purpose limitation, data minimization and data-subject rights (Regulation (EU) 2016/679). India’s Digital Personal Data Protection Act, 2023 provides a statutory framework for processing digital personal data; commencement is provision-specific by government notification, so operators must check the current commencement position and rules rather than assume every provision is in force (Government of India, 2023). In the United States, the 2018 Farm Bill contains provisions affecting agricultural research and data programs, but it is not a comprehensive federal farm-data ownership/privacy code; contracts and generally applicable privacy/security law remain important.

Good governance should make consent specific and understandable, distinguish service delivery from secondary commercial use, define retention and deletion, and provide access, correction and portability where applicable. Data-sharing contracts should specify who may combine, sell, license or train models on farm data; whether anonymization is adequate; breach notification; and how farmers can leave without losing records. Ethical AI practice calls for representative training data, evaluation by crop, geography, farm size and gender where feasible, accessible explanations, grievance channels, and human accountability. Data aggregation or federated learning can reduce raw-data transfer but does not eliminate privacy risks or power imbalances.

### 7. Policy landscape

The European Union’s CAP 2023–27 includes digitalization strategies in national CAP Strategic Plans and supports infrastructure, training, skills and precision farming investments; this is an enabling framework, not a universal direct AI subsidy (European Commission, n.d.). USDA’s Agricultural Research Service operates an AI Innovation Fund to support AI/ML in agricultural research; USDA NIFA programs also support data-science and agricultural-systems research (USDA ARS, 2026; USDA NIFA, n.d.). China’s Digital Agriculture and Rural Areas Development Plan (2019–2025) set out digital production, data-resource systems and smart management goals (Ministry of Agriculture and Rural Affairs & CAC, 2020). Kenya’s digital-agriculture strategy should be read alongside broader national digital, agricultural and e-government policy; this review did not locate a sufficiently authoritative primary source to substantiate the specific title “Kenya e-Agriculture Strategy” cited in the supplied draft, so it is not treated here as a confirmed named instrument.

Policy effectiveness depends on extension, connectivity, open infrastructure, competition and procurement standards as much as on funding AI research. Public support should favor verified public benefit, interoperability, farmer bargaining power and independently measured outcomes.

### 8. Case studies

**Case 1: John Deere See & Spray, United States.** Boom-mounted cameras and onboard vision processing classify crop versus weed, then control nozzles for targeted herbicide application. University of Arkansas researchers’ three-year soybean trial measured 43–59% lower post-emergence herbicide use; the low-sensitivity treatment also produced more Palmer amaranth, emphasizing that thresholds and weed-control outcomes require agronomic management. John Deere reported 59% average herbicide savings across >1 million acres in 2024, a company metric rather than independent randomized evidence (University of Arkansas System Division of Agriculture, 2025; John Deere, 2024). **Lesson:** edge inference can act at machine speed, but calibration, weed pressure, herbicide program and crop protection outcomes must be assessed together.

**Case 2: AI advisory and automation in low- and middle-income countries.** FAO’s 2022 technical study synthesized ten case studies across Africa, Asia and Latin America/Caribbean. It found digital solutions predominantly used smartphones/tablets and software, with high investment costs, skills and enabling policy as recurrent constraints. The report does not establish one universal yield or ROI figure; its value is comparative evidence on fit and adoption conditions (McCampbell, 2022). **Lesson:** shared access, hiring platforms, local advice and institutional support can matter more than sophisticated model choice.

**Case 3: Mobile AI advisory in Malawi (2025 reporting).** The Associated Press reported on Ulangizi, a WhatsApp-based tool used in Chichewa and English for text, voice and crop-image questions, with farmer-support agents helping users. The report describes a farmer who diversified into potatoes after advice and earned over $800 in sales; this is an individual account, not a controlled impact estimate. It also documents connectivity delays and the role of human agents. **Lesson:** multimodal/local-language interfaces can widen access, but safety, independent impact evaluation, connectivity and human escalation determine whether a pilot can scale (Associated Press, 2025).

### 9. Five-to-ten-year outlook

Likely directions include low-power edge AI for cameras and sensors; multimodal models that combine images, weather and agronomic text; privacy-aware collaborative learning; robotics and autonomous machinery; genomic prediction and automated phenotyping; and conversational advice that can operate in local languages. The World Bank identifies infrastructure, locally relevant data, skills and governance as prerequisites for equitable agricultural AI rather than optional complements (World Bank, 2025). A plausible development path is hybrid: local inference for timely decisions, cloud services for heavier analysis, and extension or agronomists for uncertain/high-consequence cases. Forecasting and generative systems must be evaluated for hallucinations, calibration, pesticide safety and unequal error rates before deployment.

### 10. Developed and developing economies

High-income economies generally have more reliable connectivity, mechanization, capital and locally collected commercial-farm data, supporting equipment-heavy PA and subscriptions. Low- and middle-income settings more often face small plots, lower device access, constrained electricity and connectivity, and fewer local training labels. These categories conceal wide differences; within-country rural access and farm size can matter more than national income. FAO’s ten-country case-study synthesis found access limitations and high costs/skills barriers for small-scale producers; the World Bank notes that data and model development often underrepresent smallholders and local crops (McCampbell, 2022; World Bank, 2025). A fair comparison therefore tracks farm-level costs, adoption, accuracy, net income, input intensity, gendered access and resilience—not just national AI market size or pilot counts.

## Discussion

Across the ten questions, the strongest conclusion is conditional: AI can improve decisions and resource targeting, but realized benefits depend on fit, validation and adoption economics. The most mature evidence concerns perception and operational tasks, such as weed sensing and variable-rate application. Farm profitability evidence is promising at pooled level but highly heterogeneous; sustainability evidence has uneven coverage and limited long-term monitoring. Case studies show that agronomy, connectivity and trusted human support remain core parts of the system.

The research gap is not another demonstration that an image classifier can reach high accuracy. Needed are multi-year comparisons across representative farms, transparent total-cost accounting, open measurement protocols, reproducible performance by subgroup and independent evaluation of environmental outcomes. Data contracts and model accountability should be included in procurement and extension programs from the start.

## Conclusions and recommendations

1. Select AI for a defined farm decision and test it against current practice with local data before scaling.
2. Report context with every claimed benefit: crop, location, year, sample, baseline, system cost, uncertainty and outcome measure.
3. Offer smallholders shared equipment, cooperatives, pay-per-use services and low-bandwidth multilingual advice; fund extension and digital skills alongside devices.
4. Require portable data, clear consent and secondary-use terms, security controls and farmer-accessible correction/deletion procedures.
5. Measure environmental outcomes directly over multiple seasons and include possible trade-offs, rather than inferring sustainability from model performance.
6. Public agencies should support interoperable infrastructure and independent evaluation while avoiding subsidies tied to a single vendor.

## References (APA 7th)

Associated Press. (2025, September 12). *How AI is helping some small-scale farmers weather a changing climate*. https://apnews.com/article/31979c49ed66b8222ea6afe7e3247770

Ben Ayed, R., & Hanana, M. (2021). Artificial intelligence to improve the food and agriculture sector. *Journal of Food Quality, 2021*, 5584754. https://doi.org/10.1155/2021/5584754

Benos, L., Tagarakis, A. C., Dolias, G., Berruto, R., Kateris, D., & Bochtis, D. (2021). Machine learning in agriculture: A comprehensive updated review. *Sensors, 21*(11), 3758. https://doi.org/10.3390/s21113758

European Commission. (n.d.). *Digitalisation: Agriculture and rural development*. Retrieved October 24, 2026, from https://agriculture.ec.europa.eu/vision-overview/digitalisation_en

European Parliament and Council of the European Union. (2016). Regulation (EU) 2016/679 (General Data Protection Regulation). https://eur-lex.europa.eu/eli/reg/2016/679/oj

Government of India. (2023). *The Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023).* https://www.indiacode.nic.in/bitstream/123456789/22037/2/a2023-22.pdf

John Deere. (2024, September 18). *See & Spray customers see 59% average herbicide savings in 2024*. https://www.deere.ca/en/news/all-news/see-spray-herbicide-savings/

Lan, J., & Ban, Q. (2025). The farm-level economic and environmental benefits of precision agriculture technology adoption: A meta-analysis of global evidence. *Sustainability, 17*(24), 11223. https://doi.org/10.3390/su172411223

McCampbell, M. (2022). *Agricultural digitalization and automation in low- and middle-income countries: Evidence from ten case studies*. FAO Agricultural Development Economics Technical Study No. 25. https://doi.org/10.4060/cc2914en

Ministry of Agriculture and Rural Affairs of the People’s Republic of China & Central Cyberspace Affairs Commission. (2020). *Development plan for digital agriculture and rural areas (2019–2025).* https://faolex.fao.org/docs/pdf/chn193207.pdf

OECD. (2022). *The digitalisation of agriculture: A literature review and emerging policy issues*. OECD Food, Agriculture and Fisheries Papers. https://doi.org/10.1787/285cc27d-en

Ruder, S.-L., Faxon, H. O., Orzel, E. C., Devkota, R., & Bronson, K. (2026). Reviewing the evidence on precision agriculture and environmental sustainability. *npj Sustainable Agriculture, 4*, Article 9. https://doi.org/10.1038/s44264-026-00128-x

United States Department of Agriculture, Agricultural Research Service. (2026). *ARS AI Innovation Fund (FY26).* https://scinet.usda.gov/opportunities/ai-innovation/

United States Department of Agriculture, National Institute of Food and Agriculture. (n.d.). *Data Science for Food and Agricultural Systems (DSFAS).* Retrieved October 24, 2026, from https://www.nifa.usda.gov/grants/programs/data-science-food-agricultural-systems-dsfas

University of Arkansas System Division of Agriculture. (2025, March 10). *Precision agriculture research measures effectiveness of See & Spray technology*. https://aaes.uada.edu/news/see-and-spray-research/

World Bank. (2025). *Digital progress and trends report 2025: Strengthening AI foundations*. https://www.worldbank.org/en/publication/dptr2025-ai-foundations/report
