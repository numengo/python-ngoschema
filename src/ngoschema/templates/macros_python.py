# *- coding: utf-8 -*- 

{% macro protected_region(region_id, pr_dict={}, comment='#') %}

{{comment}} PROTECTED REGION ID({{region_id}}) ENABLED START
{{ pr_dict.get(region_id,"") }}
{{comment}} PROTECTED REGION END
{%- endmacro %}
