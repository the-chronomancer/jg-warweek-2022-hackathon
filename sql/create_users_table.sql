CREATE TABLE users (
	user_id VARCHAR ( 36 ) PRIMARY KEY,
	first_name VARCHAR ( 50 ),
	last_name VARCHAR ( 50 ),
	email VARCHAR ( 255 ) UNIQUE,
	phone VARCHAR ( 12 )
);