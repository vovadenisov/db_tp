USE tp_hw_1;
ALTER TABLE post ADD child_posts_count INT DEFAULT 0;
ALTER TABLE followers ADD CONSTRAINT followers_follower_following_unique UNIQUE (follower_id, following_id);
ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_user_thread_unique UNIQUE (user_id, thread_id);
