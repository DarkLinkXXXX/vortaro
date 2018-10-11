create table phrase (
  dictionary text not null,

  lang_low text not null,
  lang_high text not null,
  lang_low_word text not null,
  lang_high_word text not null,
  part_of_speech text not null,

  -- lang_low is lower in alphabetical order, and
  -- lang_high is higher in alphabetical order.
  check (lang_low < lang_high)
);
create index on phrase(lang_low);
create index on phrase(char_length(lang_low));
create index on phrase(lang_high);
create index on phrase(char_length(lang_high));
create index on phrase(part_of_speech);

create view part_of_speech, lang, word as (
  select
    part_of_speech,
    lang_low as "from_lang",
    lang_high as "to_lang",
    lang_low_word as "word"
  from phrase
  union
  select
    part_of_speech,
    lang_high as "from_lang",
    lang_low as "to_lang",
    lang_high_word as "word"
  from phrase
) order by char_length(word);
