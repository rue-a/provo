```mermaid
flowchart TD
classDef entity fill:#FC766AFF
classDef entity color:333
classDef entity stroke:#FC766AFF
classDef entity stroke-width:1px
classDef activity fill:#184A45FF
classDef activity color:#eee
classDef activity stroke:#184A45FF
classDef activity stroke-width:1px
classDef agent fill:#B0B8B4FF
classDef agent color:333
classDef agent stroke:#B0B8B4FF
classDef agent stroke-width:1px
http://example.org#crimeData[<a style=color:inherit href=http://example.org#crimeData>Crime Data</a>]:::entity
http://example.org#government-. <a style=color:inherit href=https://www.w3.org/TR/prov-o/#wasAttributedTo>produced</a> .->http://example.org#crimeData
http://example.org#nationalRegionsList[<a style=color:inherit href=http://example.org#nationalRegionsList>National Regions List</a>]:::entity
http://example.org#civil_action_group-. <a style=color:inherit href=https://www.w3.org/TR/prov-o/#wasAttributedTo>produced</a> .->http://example.org#nationalRegionsList
http://example.org#aggregatedByRegions[<a style=color:inherit href=http://example.org#aggregatedByRegions>Aggregated by Regions</a>]:::entity
http://example.org#aggregationActivity-- <a style=color:inherit href=https://www.w3.org/TR/prov-o/#wasGeneratedBy>generated</a> -->http://example.org#aggregatedByRegions
http://example.org#derek-. <a style=color:inherit href=https://www.w3.org/TR/prov-o/#wasAttributedTo>produced</a> .->http://example.org#aggregatedByRegions
http://example.org#bar_chart[<a style=color:inherit href=http://example.org#bar_chart>Bar Chart</a>]:::entity
http://example.org#illustrationActivity-- <a style=color:inherit href=https://www.w3.org/TR/prov-o/#wasGeneratedBy>generated</a> -->http://example.org#bar_chart
http://example.org#derek-. <a style=color:inherit href=https://www.w3.org/TR/prov-o/#wasAttributedTo>produced</a> .->http://example.org#bar_chart
http://example.org#aggregationActivity{{<a style=color:inherit href=http://example.org#aggregationActivity>Aggregation Activity</a>}}:::activity
http://example.org#crimeData-- <a style=color:inherit href=https://www.w3.org/TR/prov-o/#used>was used by</a> -->http://example.org#aggregationActivity
http://example.org#nationalRegionsList-- <a style=color:inherit href=https://www.w3.org/TR/prov-o/#used>was used by</a> -->http://example.org#aggregationActivity
http://example.org#derek-. <a style=color:inherit href=https://www.w3.org/TR/prov-o/#wasAssociatedWith>initiated</a> .->http://example.org#aggregationActivity
http://example.org#illustrationActivity{{<a style=color:inherit href=http://example.org#illustrationActivity>Illustration Activity</a>}}:::activity
http://example.org#aggregatedByRegions-- <a style=color:inherit href=https://www.w3.org/TR/prov-o/#used>was used by</a> -->http://example.org#illustrationActivity
http://example.org#derek-. <a style=color:inherit href=https://www.w3.org/TR/prov-o/#wasAssociatedWith>initiated</a> .->http://example.org#illustrationActivity
http://example.org#government[/<a style=color:inherit href=http://example.org#government>Government</a>\]:::agent
http://example.org#civil_action_group[/<a style=color:inherit href=http://example.org#civil_action_group>Civil Action Group</a>\]:::agent
http://example.org#national_newspaper_inc[/<a style=color:inherit href=http://example.org#national_newspaper_inc>National Newspaper Inc.</a>\]:::agent
http://example.org#derek[/<a style=color:inherit href=http://example.org#derek>Derek</a>\]:::agent
http://example.org#national_newspaper_inc-. <a style=color:inherit href=https://www.w3.org/TR/prov-o/#actedOnBehalfOf>instructed</a> .->http://example.org#derek
```