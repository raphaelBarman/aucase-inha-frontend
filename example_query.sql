select o.text, MATCH(o.text) against('Portrait de femme' in boolean mode) as relevance_object,
section_texts.child_text, MATCH(section_texts.child_text) against('Couture' in boolean mode) as relevance_child_section,
section_texts.parent_text, MATCH(section_texts.parent_text) against('Couture' in boolean mode) as relevance_parent_section,
(MATCH(o.text) against('Portrait de femme' in boolean mode) +
MATCH(section_texts.child_text) against('Couture' in boolean mode) +
MATCH(section_texts.parent_text) against('Couture' in boolean mode)) as total_relevance
from object o
left join (
select s1.id as id, s1.text as child_text, s2.text as parent_text
from section s1
left join section s2 on s1.parent_section_id = s2.id) as section_texts
on o.parent_section_id = section_texts.id
where MATCH(o.text) against('Portrait de femme' in boolean mode)
and (MATCH(section_texts.child_text) against('Couture' in boolean mode) 
OR 
MATCH(section_texts.parent_text) against('Couture' in boolean mode))
order by relevance_object + relevance_child_section + relevance_parent_section desc;