# Quizmenow
#### Video Demo: https://www.youtube.com/watch?v=3lB5Ab6Wp08
#### Description:
###### General:
**WHen COVID-19 broke out in my country, I was thinking of what to do for the final project.**
**Suddenly we were on lockdown and every one had to take classes online at home.**
**But soon problems arose, when the teachers found out that they couldn't give us test sheet.**
**Therefore I decided to solve the problem by creating a platform where you can create quizes and share it with others.**
**The interface of the quiz editor is simple to use, you can create a quiz in just minutes.**

###### Create:
**Personally, I think this part is the hardest part to code of the whole program.**
**I had to figure out a way to dynamically generate a set of questions whenever the add button is pressed.**
**Also storing it in the SQL database.**
**I finished this part by setting a counter and changing the name of the tags with placeholders every time the button is clicked**
**As for the done button, it collects every input field and sent it to application.py**
**I then use a loop to save a set of questions one by one into the SQL database.**
**The first input on the page is the quiz name.**
**The 5 inputs in every set of questions are question, answer_a, answer_b, answer_c, answer_d.**
**The radio buttons are used to set the correct answer for every question,**

###### Edit:
**This is basically the combination of create and search.**
**You will see a table which show the quizes you created and the created date.**
**The edit button will let you edit the quiz you created.**
**I generated the quiz into input tags with jinja, kinda like Quiz.**
**The rest basically is the same as Create.**

###### Search:
**This is the second hardest part.**
**After typing into the search bar, it will generate a table of quizes.**
**I had to think of a way to generate a unique button for every results.**
**I finished this part by having the buttons run a function that put the id of the button you clicked into a hidden input field**
**Then I use request.form.get to get the value in the input field, and run the quiz route.**

###### Quiz:
**This is probably the easiest part of this website.**
**It generates the quiz you selected in Search.**

###### Results:
**After submitting the Quiz, I use a loop in application.py to check if the answers are correct and store the correct and incorrect in another column.**
**I then generate the results and use Jinja to check: if correct: generate "Well done!" else: generate the correct answer.**