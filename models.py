from __future__ import annotations

#from adts import List, Queue

#######################################################

## dummy data for testing purposes only:


TEST = [row.split("///") for row in '''
bob123///1///1//////A_stick_man_driving_a_car_png.png///Driving my car, brum brum!///0
bob123///2///1///1///A_stickman_riding_a_rollercoaster_png.png//////5
jeff456///3///2//////A_stickman_going_shopping_png.png///Let's all go to the mall!!!!///2
jeff456///4///2///1///A_stickman_going_to_work_png.png//////4
baz987///5///3///1///A_stickman_going_shopping_png.png//////2
baz987///6///3///2///A_stick_man_driving_a_car_png.png//////4
baz987///7///3///3///A_stick_man_going_to_the_zoo_png.png//////2'''.strip().splitlines()]

    
   
#######################################################

class PostNotFoundError(Exception):
    """Custom exception raised when a post is not found
    (symptom of a malformed database)"""

#######################################################

class Post:
    """A single node inside a thread tree"""
    def __init__(self, post_id : int, username : str,
                 image : str, caption : str, popularity: int) -> Self:
        self.__post_id = post_id
        self.__username = username
        self.__image = image
        self.__caption = caption
        self.__popularity = popularity
        self.__replies = []  # List()  ← creating your own ADT is worth more marks!
   
    def _get_post_id(self) -> int:
        """Get post id of this post"""
        return self.__post_id
    
    def _get_replies(self) -> list:
        """Return a list of this post's replies"""
        return self.__replies
    
    def _add_reply(self, reply: Self, sort_popularity: bool):
        """Add a post in reply to this post"""
        if sort_popularity:
            for index, post in enumerate(self.__replies):
                if reply.popularity >= post.popularity:
                    self.__replies.insert(index, reply)
        else:
            self.__replies.insert(0, reply)


    def _display(self, depth: int=0):
        """Recursively display this post and its replies
        - testing purposes only"""
        # print("  " * depth, f"post_id : {self.__post_id}")
        # print("  " * depth, f"username : {self.__username}")
        # print("  " * depth, f"image : {self.__image}")
        # print("  " * depth, f"caption : {self.__caption}")

        for post in self._get_replies():
            post._display(depth+1)

    def serialise(self):
        return {"post_id":self.__post_id,
                "username":self.__username,
                "image":self.__image,
                "caption":self.__caption,
                "popularity":self.__popularity,
                "replies":[reply.serialise() for reply in self.__replies]}

#######################################################

class Thread:
    """A tree of posts"""

    def __init__(self, this_post: Post):
        self.__root = this_post  # the original post in the thread
  
    def _find_post(self, parent_post_id: int):
        """Use BFS to explore the tree and locate a post"""
        posts = [self.__root] #  Queue(self.__root)  ← creating your own ADT is worth more marks!

        while posts:

            this_post = posts.pop(0) # posts.dequeue() ← creating your own ADT is worth more marks!
            this_id = this_post._get_post_id()
    
            if this_id == parent_post_id:
                return this_post
            
            for reply in this_post._get_replies():
                posts.insert(0, reply) # posts.enqueue(reply) ← creating your own ADT is worth more marks!
        
        raise PostNotFoundError(f"Could not find parent post with post_id {parent_post_id}")

    def _display(self):
        """Display this thread, starting from the root post"""
        self.__root._display()

    def serialise(self):
        return self.__root.serialise()
        

 #######################################################       

class Feed:
    """A wrapper for an array of threads..."""
    def __init__(self, data: list, sort_popularity=bool):
        self.__threads = []  # List()  ← creating your own ADT is worth more marks!
        print(data)
        for row in data:
            
            username, post_id, user_id, parent_post_id, image, caption, popularity = row
            this_post = Post(int(post_id), username, image, None if not caption else caption, int(popularity))
            
            if not parent_post_id:
                this_thread = Thread(this_post)
                self._add(this_thread)
            else:
                self._assign_reply_to_post(this_post, int(parent_post_id), sort_popularity)
            print("Added post", post_id)

    
    def _add(self, this_thread: Thread):
        """Add a thread to the feed"""
        self.__threads.insert(0, this_thread)

    def _assign_reply_to_post(self, this_post: Post,
                             parent_post_id: int,
                             sort_popularity: bool):
        """Iterate through known threads to locate
        the parent post to assign a new reply to"""
        for thread in self.__threads:
            try:
                parent_post = thread._find_post(parent_post_id)
                parent_post._add_reply(this_post, sort_popularity)
                break
            except PostNotFoundError:
                pass
        else:
            raise PostNotFoundError(f"No post found with post_id {parent_post_id}")

    def _display(self):
        """Iterate through the threads and display them"""
        
        for thread_num, thread in enumerate(self.__threads):        
            thread._display()
    
    def serialise(self):
        """Serialise Python class into a dictionary
        ready for JSON parsing"""
        return [thread.serialise() for thread in self.__threads]

#######################################################
  
if __name__ == "__main__":
    print("Testing model...")
    tree = Feed(TEST)

    tree._display()