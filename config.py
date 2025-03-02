DB_FILENAME = "db/artthreads.db"
IMAGES_DIR = "static/images"
STATUS_NOT_AUTHORISED = 511
STATUS_OK = 200

GET_POSTS_AND_VOTES_QUERY = """SELECT username, post.post_id, user.user_id, post.parent_post_id, image, caption, COALESCE(SUM(prize), 0) AS popularity
                            FROM post
                            INNER JOIN user ON post.user_id = user.user_id
                            LEFT JOIN vote ON post.post_id = vote.post_id
                            GROUP BY post.post_id, username, user.user_id, post.parent_post_id, image, caption"""

INSERT_NEW_POST_QUERY ="""INSERT INTO Post(image, user_id, parent_post_id, caption)
                        VALUES (?, ?, ?, ?) RETURNING post_id AS post_id
                        INSERT INTO Vote()"""

GET_USERNAME_AND_PASSWORD_QUERY = "SELECT user_id, password FROM user WHERE username = ?"

SUBMIT_VOTE_QUERY = """INSERT INTO vote(user_id, post_id, prize, parent_post_id)
                     VALUES (?, ?, ?, (SELECT parent_post_id
                     FROM post
                     WHERE post_id=?))
                     ON CONFLICT(user_id, prize, parent_post_id) 
                     DO UPDATE SET post_id = ?"""