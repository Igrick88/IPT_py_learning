# coding: utf8
from dataclasses import dataclass
from datetime import datetime
import csv
import configparser
from typing import List
import abc


@dataclass
class Account:
    """
    Класс - запись в адресной книге
    """
    account_id: int
    last_name: str
    first_name: str
    middle_name: str
    phone: str

    def __str__(self):
        s = f'{self.account_id},{self.last_name},{self.first_name},{self.middle_name},{self.phone}'
        return s

    def __lt__(self, other):
        return self.last_name.lower() < other.last_name.lower()

    def update_account(self):
        if self is not None:
            a = Front.ask_for_account_data()
            self.last_name = a.last_name.replace(',', ' ') or self.last_name
            self.first_name = a.first_name.replace(',', ' ') or self.first_name
            self.middle_name = a.middle_name.replace(',', ' ') or self.middle_name
            self.phone = a.phone.replace(',', ' ') or self.phone


@dataclass
class ABData:
    """
    Класс - данные адресной книги
    """
    description: str
    accounts: List[Account]


class InteractionWithFile:
    def __init__(self, file_name: str, abdata: ABData):
        self.file_name = file_name
        self.abdata = abdata

    def get_ab_from_csv(self):
        """
         Добавляет в объект типа AddressBook данные из csv файла
        :param file_name: имя файла
        :param ab: объект "Адресная книга", в которую пишутся данные из файла
        :return:
        """
        if file_name != '':
            with open(self.file_name) as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    a = Account(row['account_id'], row['last_name'], row['first_name'], row['middle_name'],
                                row['phone'])
                    self.abdata.accounts.append(a)

    def save_to_csv(self):
        """
        Сохранение в csv файл
        :param file_name: Имя файла
                     ab: Ссылка на адресную книгу
        :return:
        """
        with open(self.file_name, 'w', newline='') as csv_file:
            field_names = ['account_id', 'last_name', 'first_name', 'middle_name', 'phone']
            writer = csv.DictWriter(csv_file, fieldnames=field_names)

            writer.writeheader()
            for a in self.abdata.accounts:
                writer.writerow({'account_id': a.account_id,
                                 'last_name': a.last_name,
                                 'first_name': a.first_name,
                                 'middle_name': a.middle_name,
                                 'phone': a.phone})


class AbsCls(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'delete_account') and
                callable(subclass.delete_account) and
                hasattr(subclass, 'add_account') and
                callable(subclass.add_account) and
                hasattr(subclass, 'find_account') and
                callable(subclass.find_account))

    @abc.abstractmethod
    def delete_account(self):
        """Удалить запись"""
        raise NotImplementedError

    @abc.abstractmethod
    def add_account(self, account: Account):
        """Добавить запись"""
        raise NotImplementedError

    @abc.abstractmethod
    def find_account(self):
        """Найти запись"""
        raise NotImplementedError


class Saver(AbsCls):
    def __init__(self, file_interactor: InteractionWithFile, abdata: ABData):
        self.file_interactor = file_interactor
        self.abdata = abdata

    def delete_account(self, account: Account):
        """
        Удаляет запись из адресной книги
        :return: None
        """
        if account is not None:
            for i, cur_account in enumerate(self.abdata.accounts):
                if account.account_id == cur_account.account_id:
                    del self.abdata.accounts[i]
                    break
            self.file_interactor.save_to_csv()
            Front.show_record_deleted(account)

    def add_account(self, account: Account):
        """
        Добавляет запись в адресную книгу
        :return: None
        """
        self.abdata.accounts.append(account)
        self.file_interactor.save_to_csv()
        Front.show_record_saved(account)

    def find_account(self):
        """
        Поиск записей по начальным буквам фамилии (регистронезависимый)
        :return: Найденные записи
        """
        accounts = []
        inputed = Front.ask_for_lastname_beginning()
        for account in self.abdata.accounts:
            if account.last_name.lower().startswith(inputed.lower()):
                accounts.append(account)
        return sorted(accounts)


class ABService:
    """
    Класс - интерфейс к адресной книге
    """

    def __init__(self, saver: AbsCls):
        """
        Привязка ABService к saver'у
        :param saver:
        """

        self.saver = saver

    def delete_account(self, account):
        self.saver.delete_account(self, account)

    def add_account(self, account):
        """
        Добавление новой записи в адресную книгу
        :return: None
        """
        self.saver.add_account(account)

    def find_account(self):
        """
        Поиск записей по начальным буквам фамилии (регистронезависимый)
        :return: Найденные записи
        """

        return self.saver.find_account()


class Front:
    def __init__(self, abdata: ABData):
        """
        Привязка ABService к saver'у
        :param abdata:
        """

        self.abdata = abdata

    @classmethod
    def ask_for_mode(cls):
        """
        Спросить у пользователя, что нужно сделать
        :return: Буква выбора (п, д, и, у, н, в)
        """
        print()
        print('Выберите действие:')
        print('п - просмотр всей книги, \nд - добавить запись, \nи - изменить запись,\
        \nу - удалить запись, \nн - найти запись, \nв - выход')
        choice = input()
        return choice

    def show_address_book(self):
        """
        Просмотр адресной книги
        :return: None
        """
        print('=' * len(self.abdata.description))
        print(self.abdata.description)
        print('=' * len(self.abdata.description))

        for a in sorted(self.abdata.accounts):
            print(f'{a.last_name} {a.first_name} {a.middle_name} | {a.phone}')

    def ask_for_account_data(self):
        """
        Добавление новой записи в адресную книгу
        :return:
        """
        last_name = input('Введите фамилию: ').replace(',', ' ')
        first_name = input('Введите имя: ').replace(',', ' ')
        middle_name = input('Введите отчество: ').replace(',', ' ')
        phone = input('Введите телефон: ').replace(',', ' ')
        account_id = int(datetime.now().timestamp())
        acc_fields = {'account_id': account_id,
                      'last_name': last_name,
                      'first_name': first_name,
                      'middle_name': middle_name,
                      'phone': phone}
        return acc_fields

    @classmethod
    def choose_only_one_line(cls, accounts):
        """
        Выбрать из нескольких записей адресной книги одну
        :param accounts: Набор записей, из которых надо выбрать
        :return: Возврат выбранной записи или None
        """
        i = 1
        for a in accounts:
            print(f'{i}. {a.last_name} {a.first_name} {a.middle_name} | {a.phone}')
            i += 1
        num = int(input('Введите номер нужной записи: '))
        if num in range(1, len(accounts) + 1):
            return accounts[num - 1]
        else:
            print('Неправильно указан номер')
            return None

    @classmethod
    def confirm_account(cls, accounts, mode='у'):
        """
        Запрашивает у пользователя подтверждение на измение/удаление записи
        :return: account
        """
        action = {'noun': 'Удаление', 'verb': 'Удалить'}
        if mode.lower() == 'и':
            action['noun'] = 'Изменение'
            action['verb'] = 'Изменить'
        print(f'{action["noun"]} записи')

        if len(accounts) == 1:
            account = accounts[0]
            confirm = input(f'{action["verb"]}: "{account}" ? (д/н)')
            if confirm.lower() == 'д':
                return account
            else:
                return None
        elif len(accounts) > 1:
            print('Найдено более одной записи:')
            return Front.choose_only_one_line(accounts)
        elif len(accounts) == 0:
            print('Ничего не найдено')
            return None

    @classmethod
    def ask_for_lastname_beginning(cls):
        return input('Введите начало фамилии для поиска: ')

    @classmethod
    def show_record_deleted(cls, account: Account):
        print(f'Запись "{account}" удалена')

    @classmethod
    def show_record_saved(cls, account: Account):
        print(f'Запись "{account}" сохранена')


def menu(choice, abservice: ABService, front: Front):
    while True:
        if choice.lower() == 'п':
            front.show_address_book()
        elif choice.lower() == 'д':
            acc_fields = front.ask_for_account_data()
            acc = Account(acc_fields['account_id'], acc_fields['last_name'], acc_fields['first_name'],
                              acc_fields['middle_name'], acc_fields['phone'])
            abservice.add_account(acc)
        elif choice.lower() == 'и':
            account_to_update = Front.confirm_account(abservice.find_account(), mode='и')
            if account_to_update is not None:
                account_to_update.update_account()
                InteractionWithFile.save_to_csv(address_book, file_name)
        elif choice.lower() == 'у':
            account_to_delete = Front.confirm_account(address_book.find_account(), mode='у')
            if account_to_delete is not None:
                address_book.delete_account(account_to_delete)
                InteractionWithFile.save_to_csv(address_book, file_name)
        elif choice.lower() == 'н':
            accounts = abservice.find_account()
            for account in accounts:
                print(account)
            if len(accounts) == 0:
                print('Ничего не найдено')
            print()
        elif choice.lower() == 'в':
            break
        choice = Front.ask_for_mode()


# file_name = 'address_book.csv'
# parser = argparse.ArgumentParser(description="Записная книжка содержит записи \
# в формате id,Фамилия,Имя,Отчество,Телефон")
# parser.add_argument('-m', '--mode', default='m')
# args = parser.parse_args()


def get_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config


def get_settings(path, section, setting):
    config = get_config(path)
    value = config.get(section, setting)
    return value


path = 'settings.ini'
file_name = get_settings(path, 'Settings', 'address_book_file')
ab_description = get_settings(path, 'Settings', 'description')
mode = get_settings(path, 'Settings', 'mode')

ab = ABData(description=ab_description, accounts=[])
interactor = InteractionWithFile(file_name, ab)
interactor.get_ab_from_csv()
saver = Saver(interactor, ab)
abservice = ABService(saver)
front = Front(ab)

menu(mode, abservice, front)
