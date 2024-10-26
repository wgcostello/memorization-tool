import sqlalchemy
from sqlalchemy.ext import declarative
from sqlalchemy import orm

engine = sqlalchemy.create_engine(
    'sqlite:///flashcard.db?check_same_thread=False'
)

Base = declarative.declarative_base()


class Flashcards(Base):
    __tablename__ = 'flashcard'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    question = sqlalchemy.Column(sqlalchemy.String)
    answer = sqlalchemy.Column(sqlalchemy.String)
    box_number = sqlalchemy.Column(sqlalchemy.Integer)


Base.metadata.create_all(engine)

Session = orm.sessionmaker(bind=engine)
session = Session()


def get_user_input(prompt, accept_blank=False):
    while True:
        user_input = input(prompt).strip()
        if user_input or accept_blank:
            return user_input


class FlashcardMaker:
    def __init__(self):
        self.unknown_command = True
        self.adding_flashcards = False
        self.practising_flashcard = False
        self.updating_flashcard = False
        self.learning_flashcard = False

        self.main_menu()

    def main_menu(self):
        while self.unknown_command:
            user_input = get_user_input('1. Add flashcards\n'
                                        '2. Practice flashcards\n'
                                        '3. Exit\n')
            if user_input == '1':
                self.unknown_command = False
                self.adding_flashcards = True
                self.add_flashcard_menu()
            elif user_input == '2':
                self.unknown_command = False
                self.practise_flashcards()
            elif user_input == '3':
                self.unknown_command = False
                print('Bye!')
                exit()
            else:
                print(f'{user_input} is not an option')

    def add_flashcard_menu(self):
        while self.adding_flashcards:
            user_input = get_user_input('1. Add a new flashcard\n'
                                        '2. Exit\n')
            if user_input == '1':
                question = get_user_input('Question:\n')
                answer = get_user_input('Answer:\n')
                new_data = Flashcards(question=question, answer=answer,
                                      box_number=1)
                session.add(new_data)
                session.commit()
            elif user_input == '2':
                self.adding_flashcards = False
                self.unknown_command = True
                self.main_menu()
            else:
                print(f'{user_input} is not an option')

    def practise_flashcards(self):
        # Get all entries from the flashcard table
        result_list = session.query(Flashcards).all()
        if not result_list:
            print('There is no flashcard to practice!')

        for flashcard in result_list:
            self.practising_flashcard = True
            while self.practising_flashcard:
                print(f'Question: {flashcard.question}')
                choice = get_user_input('press "y" to see the answer:\n'
                                        'press "n" to skip:\n'
                                        'press "u" to update:\n')
                if choice == 'y':
                    print(f'Answer: {flashcard.answer}')
                    self.practising_flashcard = False
                    self.learning_flashcard = True
                    self.learn_flashcard(flashcard)
                elif choice == 'n':
                    self.practising_flashcard = False
                elif choice == 'u':
                    self.practising_flashcard = False
                    self.updating_flashcard = True
                    self.update_flashcard(flashcard)
                else:
                    print(f'{choice} is not an option')

        else:
            self.unknown_command = True
            self.main_menu()

    def update_flashcard(self, flashcard):
        while self.updating_flashcard:
            choice = get_user_input('press "d" to delete the flashcard:\n'
                                    'press "e" to edit the flashcard:\n')
            if choice == 'd':
                session.delete(flashcard)
                session.commit()
                self.updating_flashcard = False

            elif choice == 'e':
                print(f'current question: {flashcard.question}')
                new_question = get_user_input(
                    'please write a new question:\n', accept_blank=True
                )
                if new_question:
                    flashcard.question = new_question

                print(f'current answer: {flashcard.answer}')
                new_answer = get_user_input(
                    'please write a new answer:\n', accept_blank=True
                )
                if new_answer:
                    flashcard.answer = new_answer

                session.commit()
                self.updating_flashcard = False

            else:
                print(f'{choice} is not an option')

    def learn_flashcard(self, flashcard):
        while self.learning_flashcard:
            choice = get_user_input('press "y" if your answer is correct:\n'
                                    'press "n" if your answer is wrong:\n')
            if choice == 'y':
                if flashcard.box_number == 3:
                    session.delete(flashcard)
                else:
                    flashcard.box_number += 1
                session.commit()
                self.learning_flashcard = False

            elif choice == 'n':
                flashcard.box_number = 1
                session.commit()
                self.learning_flashcard = False

            else:
                print(f'{choice} is not an option')


if __name__ == '__main__':
    flashcard_maker = FlashcardMaker()
