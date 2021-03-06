USE tp_hw_1;
ALTER TABLE user ADD INDEX user_name_index (name);
ALTER TABLE forum ADD INDEX forum_short_name_index (short_name, id);
ALTER TABLE post ADD INDEX hierarchy_cover_index (id, hierarchy_id, child_posts_count);
ALTER TABLE followers ADD INDEX followers_followings_id_index (following_id, follower_id);
ALTER TABLE subscriptions ADD INDEX subscriptions_thread_user_index (thread_id, user_id);
ALTER TABLE post ADD INDEX post_forum_id_date_index (forum_id, date);
ALTER TABLE user ADD INDEX user_id_name_index (id, name);
ALTER TABLE thread ADD INDEX thread_forum_id_date_index (forum_id, date);
ALTER TABLE thread ADD INDEX thread_user_id_date_index (user_id, date);
ALTER TABLE post ADD INDEX post_thread_id_date_index (thread_id, date);
ALTER TABLE post ADD INDEX post_thread_id_hierarchy_index (thread_id, hierarchy_id);
ALTER TABLE post ADD INDEX post_user_id_date (user_id, date);

