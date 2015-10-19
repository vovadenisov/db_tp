USE tp_hw_1;
CREATE TABLE post_hierarchy_utils
(
  id INT NOT NULL AUTO_INCREMENT,
  forum_id INT NOT NULL,
  head_posts_number INT NOT NULL DEFAULT 0,

  PRIMARY KEY(id),
  CONSTRAINT post_hierarchy_utils_forum_id_foreign_key FOREIGN KEY(forum_id) REFERENCES forum(id) ON DELETE  CASCADE ON UPDATE CASCADE
) ENGINE=INNODB;


