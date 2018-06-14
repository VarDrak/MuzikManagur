import os
import Core
import curses

__version__ = 0.2


def Main():
    print('Welcome to MuzikManagur.')
    print('Initializing....')

    session_log = Core.CoreLog(rlog='MuzikManagur Initializing via Commander.')

    krun = True
    while krun:
        print('*'*20)
        print('*'*20)
        print('What would like you do?')
        print('reOrder folder')
        print('View session log')
        print('Save session log')
        print('QUIT')
        print('*'*20)

        choice = input('Make a selection.')
        if choice == 'QUIT':
            krun = False
        elif choice == 'O':
            print('Loading...')
            reorder_folder(session_log)
        elif choice == 'V':
            for i in range(0, len(session_log.rlog)):
                print(session_log.rlog[i])
        elif choice == 'S':
            print('Saving...')
            session_log.save_log()


def reorder_folder(session_log):
    session_log.rlog = 'Starting Commander.reorder_folder().'

    print('\n' + '*'*20)
    folder1 = None
    folder2 = None
    filename_format = ['ALBUMARTIST', '/', 'ALBUM', '/',
                       'TRACKNUMBER', '. ', 'TITLE']

    krun = True
    while krun:
        print('Folder to re-order from is:  ' + str(folder1))
        print('Folder to re-order to is:  ' + str(folder2))
        print('Current filename format is:')
        print(filename_format)
        print('*'*20)
        print('What do you wish to do?')
        print('pick Source folder for re-ordering.')
        print('pick Destination folder for re-ordering.')
        print('select Formatting for filenames.')
        print('Begin reordering.')
        print('QUIT')

        choice = input('Choose a command to execute:')
        if choice == 'QUIT':
            krun = False
        # Source folder to re-order.
        elif choice == 'S':
            while True:
                astr = ''
                try:
                    astr = \
                        str(input('Please enter the folder to re-order from.'))
                except:
                    print('Error.  Cannot load ' + astr)
                    print('Trying again.\nType [N] to stop.')
                else:
                    if astr == 'N':
                        break
                    session_log.rlog = 'Source folder changed from ' + \
                                       str(folder1) + ' to ' + str(astr)
                    folder1 = astr
                    break
        # Edit the re-ordering format.
        elif choice == 'F':
            while True:
                print('-'*20)
                print('Current filename format is:')
                print(filename_format)
                print('File output will look something like...')

                try:
                    print(Core.MuzikArkive.filename_formatter('./', './',
                                                              filename_format,
                                                              './test.opus'))
                except:
                    print('filename_formatter() just failed.')
                break
        # Destination folder to re-order.
        elif choice == 'D':
            while True:
                astr = ''
                try:
                    astr = str(input('Please enter the folder to re-order to.'))
                except:
                    print('Error.  Cannot load ' + astr)
                    print('Trying again.\nType [N] to stop.')
                else:
                    if astr == 'N':
                        break
                    session_log.rlog = 'Destination folder changed from ' + \
                                       str(folder2) + ' to ' + str(astr)
                    folder2 = astr
                    break
        # Begin re-ordering.
        elif choice == 'B':
            try:
                session_log.rlog = 'Starting reorder_folder() from Commander.'
                Core.MuzikArkive.reorder_folder(folder1, folder2,
                                                session_log, filename_format)
            except Core.CoreError as er:
                session_log.elog = 'reorder_folder() failed.'
                session_log.rlog = 'reorder_folder() failed.'
                session_log.elogger(er.elog)
                print('*^-'*20)
                print('*^-' * 20)
                print('Core.CoreError!! Last entry:')
                temp = er.elog.pop()
                print(temp)

            else:
                session_log.rlog = 'reorder_folder() from Commander finished.'
                print('Job completed.')

        else:
            print(choice + '  was not a valid option.\nPlease try again.')


def curse_control():
    stdscr = curses.initscr()


Main()
