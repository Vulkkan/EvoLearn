
<script>
document.addEventListener('DOMContentLoaded', function () {
    let score = 0;
    let currentQuestionIndex = 0;
    const totalQuestions = {{ mcqs|length }};
    const questions = {{ mcqs|tojson }};
    const userAnswers = [];

    const questionContainer = document.querySelector('.question-container');
    const scoreDisplay = document.getElementById('score');

    function displayQuestion(index) {
        if (index >= totalQuestions) {
            displayResults();
            hideScore();
            return;
        }

        const question = questions[index];
        questionContainer.innerHTML = `
            <div class="quiz-cards">
                <div class="contents">
                    <p>Question ${index + 1} of ${totalQuestions}</p>
                    <p>${question[1][0]}</p>
                    <ol class="numbered-list">
                        ${question[1][1].map((option, i) => `
                            <div class="btn-container">
                                <button class="answer-btn" data-option="${String.fromCharCode(65 + i)}" data-correct-answer="${question[1][2]}">
                                    ${String.fromCharCode(65 + i)}. ${option}
                                </button>
                            </div>
                        `).join('')}
                    </ol>
                </div>
            </div>
        `;
    }

    function displayResults() {
        let resultsHTML = `
            <p class="scoretext">Quiz completed!</p>
            <p class="finalscore">Final Score: ${score}/${totalQuestions * 10}</p>
            <div class="results-container">
        `;
        userAnswers.forEach((answer, index) => {
            const question = questions[index];
            resultsHTML += `
                <div class="quiz-cards">
                    <div class="contents">
                        <p>${question[1][0]}</p>
                        <ol class="numbered-list">
                            ${question[1][1].map((option, i) => `
                                <div class="btn-container">
                                    <button class="answer-btn ${answer.selectedOption === String.fromCharCode(65 + i) ? (answer.isCorrect ? 'correct' : 'incorrect') : ''}" data-option="${String.fromCharCode(65 + i)}">
                                        ${String.fromCharCode(65 + i)}. ${option}
                                    </button>
                                </div>
                            `).join('')}
                        </ol>
                        <p>Your answer: ${answer.selectedOption} ${answer.isCorrect ? '(Correct)' : '(Wrong)'}</p>
                        <p>Correct answer: ${answer.correctAnswer}</p>
                    </div>
                </div>
            `;
        });
        resultsHTML += `</div>`;

        // Calculate percentage score
        const percentageScore = (score / (totalQuestions * 10)) * 100;

        // Determine and append message based on score percentage
        let message = '';
        if (percentageScore === 100) {
            message = "Congratulations! You scored 100%! Perfect!";
        } else if (percentageScore >= 90) {
            message = "Excellent! You scored above 90%!";
        } else if (percentageScore >= 80) {
            message = "Well done! You scored above 80%!";
        } else if (percentageScore >= 70) {
            message = "Good job! You scored above 70%!";
        } else if (percentageScore >= 60) {
            message = "Nice work! You scored above 60%!";
        } else {
            message = "You can do better next time. Keep practicing!";
        }

        resultsHTML += `<p>${message}</p>`;

        questionContainer.innerHTML = resultsHTML;
    }


    function hideScore() {
        scoreDisplay.style.display = 'none';
    }

    displayQuestion(currentQuestionIndex);

    questionContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('answer-btn')) {
            const selectedOption = event.target.dataset.option;
            const correctAnswer = event.target.dataset.correctAnswer;
            const isCorrect = selectedOption === correctAnswer;
            userAnswers.push({
                selectedOption,
                correctAnswer,
                isCorrect
            });

            if (isCorrect) {
                event.target.classList.add('correct');
                event.target.textContent += ' (Correct)';
                score += 10;
            } else {
                event.target.classList.add('incorrect');
                event.target.textContent += ' (Wrong)';
            }

            scoreDisplay.textContent = `Score: ${score}/${totalQuestions * 10}`;
            setTimeout(() => {
                currentQuestionIndex++;
                displayQuestion(currentQuestionIndex);
            }, 2000);  // Adjust the timeout duration as needed
        }
    });
});
</script>