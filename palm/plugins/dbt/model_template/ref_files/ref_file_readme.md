# How to use --ref-file

## Docs
- Optional

``` sql
/*
## Business Definition
[put your developer notes here, write in markdown formatting]

## Developer Notes
[put your developer notes here, write in markdown formatting]
*/
```

## Select Statement
- Only the final select query is analyzed and parsed

``` sql
  distinct do.id as salesforce_opportunity_id -- description
  , do.location__c location__c -- description
  , do.state_code -- description
  , do.state as state
  , coalesce(
      sp.msa_signed_date
      , sm.sales_member_created_at
    ) as msa_signed_date -- description
  , coalesce(sp.msa_signed_date, sm.sales_member_created_at) as msa_signed_date -- description
FROM
  dim_order do
LEFT JOIN sales_member sm ON
  do.sales_member_id = sm.id
```
