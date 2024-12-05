CREATE TABLE ad_user(
	domain text NOT NULL,
	dn text PRIMARY KEY,
	samaccountname text NOT NULL,
	lastlogontimestamp timestamp with time zone,
	givenname text,
	sn text,
	mail text,
	isDisabled boolean,
	department text,
	memberof text[],
	pwdlastset timestamp with time zone,
	whencreated timestamp with time zone,
	whenchanged timestamp with time zone,
	accountexpires timestamp with time zone,
	entrydate timestamp default now()
);

COMMENT ON COLUMN ad_user.pwdlastset IS 'NULL represents set by admin';
COMMENT ON COLUMN ad_user.accountexpires IS 'NULL represents account does not expire';
COMMENT ON COLUMN ad_user.isDisabled IS 'Is ADS_UF_ACCOUNTDISABLE set in userAccountControl attribute?';
COMMENT ON COLUMN ad_user.entrydate IS 'when this row was written';

CREATE INDEX ad_user_memberof_idx ON ad_user USING gin (memberof);
