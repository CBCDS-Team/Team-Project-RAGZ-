#### Cat Datebase Monitoring System (Database Design – SQLite)

#### Database Name: cat_behaviour_database.db

This system monitors Diesel’s behaviour across:

* 🚽 Litter box visits

* 🍽 Food intake

* 💧 Water intake

* 🙈 Hiding behaviour

#### Why SQLite is used:

* Lightweight and embedded

* Serverless – no separate database server required

* Suitable for IoT and small-scale monitoring systems

* Supports relational integrity for multi-cat tracking

```Tables & Purpose
cats – Stores cat info (name, weight, joined timestamp)
litter_events – Logs litter box visits with duration and abnormal detection (≥600s flagged)
food_intake – Tracks feeding events (<20g or >100g flagged)
water_intake – Tracks drinking duration (>120s flagged)
hiding_events – Records hiding behaviour (≥900s flagged)

Relationships: One cat → Many events (1:N)
```

#### Analytics & Reporting

* Average durations, totals, and abnormal counts

* Health warnings for unusual behaviour

* CSV export for reporting

#### Examples of alerts:

* Long litter visits 😼

* Low/excessive food 😹

* Excessive drinking 🐾