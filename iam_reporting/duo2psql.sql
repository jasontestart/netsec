CREATE TABLE duo_user(
        username text PRIMARY KEY,
        is_enrolled boolean default false,
        status text,
        created date,
        last_login timestamp
);

CREATE TABLE duo_phone(
        number text,
        username text,
        capabilities text[],
        platform text,
        type text
);
