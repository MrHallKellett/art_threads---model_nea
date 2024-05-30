function get_feed()
{
    return new Promise((resolve, reject) =>
    {
        let xhr = new XMLHttpRequest();
        data = null;
        xhr.open('GET', '../get_feed', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onload = function()
        {
            if (xhr.status === 200)
            {
                data = JSON.parse(xhr.responseText);
                resolve(data);
            }
            else
            {
                reject(xhr.status);
            }
        };
        xhr.send();
    })
}

function explore_replies(post, previous_ul, original_post=false)
{
    let caption = "";
    if (original_post) { caption = post.caption}

    let ul = document.createElement("ul")
    ul.innerHTML = `<li>
                        <img src="static/images/${post.image}" width="150"/>
                            by ${post.username} ${caption}
                    </li>`

    previous_ul.appendChild(ul)
    for (const reply of post.replies)
    {
        explore_replies(reply, ul)    
    }
}

function load_feed()
{
    get_feed().then(feed_json =>
    {
        for (const thread of feed_json)
        {
            explore_replies(thread, document.body, original_post=true)          
        }
    }).catch(error =>
        console.log(error)
    )
}


