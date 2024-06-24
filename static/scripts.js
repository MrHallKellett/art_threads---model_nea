in_reply_to = null;

function submit_new_post(upload_form, in_reply_to="") {
    // Create a new FormData object from the form
    const form_data = new FormData(upload_form);
  
    // Create a new XMLHttpRequest object
    const xhr = new XMLHttpRequest();
  
    // Set the request method and URL
    xhr.open('POST', `/new_post/${in_reply_to}`, true);
  
    // Set the appropriate headers
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
  
    // Define the callback function to handle the server response
    xhr.onreadystatechange = function() {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        // Handle the successful response
        console.log(xhr.responseText);
      } else {
        // Handle the error response
        console.error(xhr.statusText);
      }
    };
  
    // Send the form data
    xhr.send(upload_form);
  }


function get_request(route)
{
    console.log("sending GET request..")
    return new Promise((resolve, reject) =>
    {
        let xhr = new XMLHttpRequest();
        data = null;
        xhr.open('GET', route, true);
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

    ul.addEventListener('click', function() { open_vote_modal(post) });
    previous_ul.appendChild(ul)
    for (const reply of post.replies)
    {
        explore_replies(reply, ul)    
    }
}

function load_feed()
{
    get_request("../get_feed").then(feed_json =>
    {
        for (const thread of feed_json)
        {
            explore_replies(thread, document.body, original_post=true)   
            let horiz_rule = document.createElement("hr")
            document.body.appendChild(horiz_rule)       
        }
    }).catch(error =>
        console.log(error)
    )
}

function open_vote_modal(this_post)
{
    console.log("openining vote modal")
    in_reply_to = this_post.post_id;
    console.log("logged that post being replied to is", in_reply_to)
    const vote_for_container = document.querySelector("div#vote_for_container").innerHTML = this_post.innerHTML;
    voting_modal.showModal();
}


function process_vote(event)
{
    const rank = event.target.name.slice(-1);
    console.log("processing vote")
    get_request(`../submit_vote/${in_reply_to}/${rank}`).then(vote_feedback =>
    {
        vote_feedback_holder.innerHTML = vote_feedback
    }).catch(error => console.log(error))

} 

const new_thread_modal = document.querySelector("dialog#new_thread_modal");
const voting_modal = document.querySelector("dialog#voting_modal");
const new_thread_button = document.querySelector("button#new_thread_btn");
const close_reply_button = document.querySelector("button#close_reply_btn");
const close_vote_button = document.querySelector("button#close_vote_btn");
const vote_1st_button = document.querySelector("button#vote_1st_place_btn")
const vote_2nd_button = document.querySelector("button#vote_2nd_place_btn")
const vote_3rd_button = document.querySelector("button#vote_3rd_place_btn")
const vote_feedback_holder = document.querySelector("span#vote_feedback_holder")

new_thread_button.addEventListener("click", () => {
    dialog.showModal();
});

close_vote_button.addEventListener("click", () => {
    voting_modal.close();
});

// "Show the dialog" button opens the dialog modally
vote_1st_button.addEventListener('click', (event) => { process_vote(event) });
vote_2nd_button.addEventListener('click', (event) => { event.preventDefault(); process_vote(event) });
vote_3rd_button.addEventListener('click', (event) => { event.preventDefault(); process_vote(event) });