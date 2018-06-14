"""Core functionality of the Muzik Managur suite.

Classes:

    MuzikArkive
    CoreError
    CoreLog

"""

import os
import taglib
import datetime

__version__ = 0.2


class MuzikArkive:
    """Create, edit, manage, and delete muzik arkives.

    Functions:

        induct_folder
        rename_file
        reorder_folder
        filename_formatter

    Class Variables:

        file_types -- list of music file-type extensions currently
         supported.
        illegal_name_characters -- string characters that should not
         be in a filename.
    """

    file_types = ['opus', 'ogg', 'flac', 'mp3', 'wma', 'wav']
    illegal_name_characters = ['/', '\\', '?', '%', '*',
                               ':', '|', '"', '<', '>']

    def __init__(self, directory, alog):
        folders = []
        files = []

        try:
            MuzikArkive.induct_folder(directory, alog, folders, files)
        except CoreError:
            raise CoreError('induct() for MuzikArkive.__init__ failed.')

        folders.sort()
        files.sort()

        self.root_folder = directory



    @staticmethod
    def induct_folder(directory, alog, fold=None, file=None):
        """Scan a folder and return the list of sub-folders and files.

        Uses full path names for both folders and files, with directory
        as working directory, aka ./
        e.g.  ./a folder/    ./a folder/another folder/a_file.extension

        Mandatory Arguments:

            directory -- the folder to scan/induct.
            alog -- CoreLog to keep track of function flow and errors.

        Optional Arguments:

            fold -- a list of folders
            file -- a list of files

        Returns:

            [
            folders -- a list of folders
            files -- a list of files
            ]
        """

        #  Some error checking against a legitimate directory.
        if not type(directory) is str:
            raise CoreError('Directory was not a string value, aborting.')
        try:
            dir_contents = os.listdir(directory)
        except:
            raise CoreError('Failed to load directory: ' + directory)

        if fold is None:
            folders = []
        else:
            folders = fold

        if file is None:
            files = []
        else:
            files = file

        alog.rlog = 'Beginning to induct ' + directory
        alog.rlog = str(len(dir_contents)) + ' items to induct.'

        #  Begin induction.
        #  Checks for folder first, then file.
        #  Folders are recursively inducted.
        #  Files must be of type MuzikArkive.file_types .
        for i in range(0, len(dir_contents)):
            if os.path.isdir(directory + dir_contents[i]):
                fullpath = os.path.join(directory + dir_contents[i]) + '/'
                folders.append(fullpath)
                try:
                    MuzikArkive.induct_folder(fullpath, alog, folders, files)
                except CoreError as er:
                    alog.elog = [
                        'Recursive induct_folder() call failed for: '
                        + fullpath,
                        er.elog
                        ]

            elif os.path.isfile(directory + dir_contents[i]):
                head, tail = os.path.split(dir_contents[i])
                tails = tail.split('.')
                if tails[len(tails) - 1] in MuzikArkive.file_types:
                    files.append(directory + dir_contents[i])

        alog.rlog = 'Finished induction.'
        return [folders, files]

    @staticmethod
    def rename_file(source, destination, alog):
        """Rename a file.

        Uses the full path name.  Therefore the file may be placed in a new
        folder as well as just renamed.
        e.g. original folder/file2rename.ext -> new_folder/new name.extension

        Arguments:

            source -- the file to be renamed.
            destination -- the new file name.
        """

        #  Some error checking against a legitimate source & destination.
        if not type(source) is str:
            raise CoreError('Source is not of str type.')
        elif not type(destination) is str:
            raise CoreError('Destination is not of str type.')
        elif not os.path.isfile(source):
            raise CoreError(source + ' is not a valid file.')

        head, tail = os.path.split(destination)
        if not os.path.isdir(head + '/'):
            try:
                os.makedirs(head + '/')
            except:
                raise CoreError('Failed to create new directory: '
                                + (head + '/'))

        for i in range(0, len(MuzikArkive.illegal_name_characters)):
            if MuzikArkive.illegal_name_characters[i] in tail:
                tail = tail.replace(MuzikArkive.illegal_name_characters[i], '_')
                alog.rlog = MuzikArkive.illegal_name_characters[i] \
                            + '  was removed from ' + destination

        if not os.path.isfile(destination):
            try:
                os.rename(source, destination)
            except:
                raise CoreError('os.rename() Failed.')
        else:
            head, tail = destination.rsplit('.', 1)
            rname = True
            i = 1
            while rname:
                addon = '[' + str(i) + '].'
                if not os.path.isfile(head + addon + tail):
                    try:
                        os.rename(source, (head + addon + tail))
                    except:
                        raise CoreError('os.rename() Failed.')
                    else:
                        rname = False
                else:
                    i += 1

    @staticmethod
    def reorder_folder(source, destination, alog, order_format=None):
        """Reorder/Reorganize a folder into another one(new or existing).

        Essentially a large batch run of MuzikArkive.rename_file .
        Though files can be renamed based on user-defined tag orders,
        as well as by destination.
        """

        #  Induct the folder first to begin reordering.
        try:
            alog.rlog = 'reorder_folder() calling induct_folder().'
            folders, files = MuzikArkive.induct_folder(source, alog)
        except CoreError as er:
            er.elog = 'induct_folder() failed.'
            raise er

        alog.rlog = str(len(files)) + ' files to re-order.'

        #  Now the actual reordering happens, one item at a time.
        #  Due to potentially high number of reorders, errors do not
        #  stop the process, the item in question is skipped.
        #  Errors are counted, so user intervention can be an option
        #  should a high number occur.
        er_count = 0
        for i in range(0, len(files)):
            try:
                alog.rlog = 'Formatting new name for ' + files[i]
                new_name = MuzikArkive.filename_formatter(
                    source, destination, files[i], order_format)
            except CoreError as er:
                er_count += 1
                alog.elog = 'filename_formatter() failed on file: ' + files[i] \
                            + '   Error count at: ' + str(er_count)
                alog.elogger(er.elog)
            else:
                try:
                    alog.rlog = 'Renaming ' + files[i]
                    MuzikArkive.rename_file(files[i], new_name, alog)
                except CoreError as er:
                    er_count += 1
                    alog.elog = 'rename_file() failed on file: ' + files[i] \
                                + '   Error count at: ' + str(er_count)
                    alog.elogger(er.elog)

            #  Should 10 errors occur, the user shall be notified, and
            #  allowed to continue, abort, or view what errors have
            #  occurred during reordering.
            if er_count > 10:
                print('!'*20)
                print('10 rename fails have occurred.\nContinue?')

                while True:
                    option = input('Yes\nNo\nShow fail renames')
                    if option == 'Y':
                        er_count = 0
                        break
                    elif option == 'N':
                        raise CoreError(
                            'User terminated:  Multiple rename fails.'
                        )
                    elif option == 'S':
                        print('-'*20)
                        for i in range(0, len(alog.elog)):
                            print(alog.elog[i])
                        print('-'*20)

        alog.rlog = 'reorder_folder completed.'

    @staticmethod
    def filename_formatter(source, destination, file, order_format):
        """Format the the filename based on song tags.

        Formats the new filename for the song file based on a format
        supplied by the function caller.
        Also checks each portion of the new filename for illegal
        characters and removes them if needed.

        Arguments:

            source -- So far not used.  May need deletion.
            destination -- Root hierarchy of full path name.  May also
                            need deletion.
            file -- The file whose full path name needs formatting.
            order_format -- The format to be used in filename formatting.

        Returns:
             The new formatted filename.
        """

        # Attempt loading taglib.
        try:
            song = taglib.File(file)
        except:
            raise CoreError('taglib.File() failed.')

        # Begin formatting the filename.
        new_name = destination
        for i in range(0, len(order_format)):
            # If next item is a tag, this block will execute.
            try:
                sub_name = song.tags[order_format[i]][0]
                # Clear filename of any illegal characters.
                for j in range(0, len(MuzikArkive.illegal_name_characters)):
                    if MuzikArkive.illegal_name_characters[j] in sub_name:
                        sub_name = sub_name.replace(
                            MuzikArkive.illegal_name_characters[j], '_'
                        )
                new_name += sub_name
            # If next item is a char or string, this block will execute.
            except:
                new_name += order_format[i]

        # Add the files extenstion to the new name formatting.
        new_name += '.' + file.rsplit('.', 1)[1]

        song.close()
        return new_name


class CoreError(Exception):
    """A base Error class for Core module.

    Any function or class within the Core module that encounters a problem
    will raise this exception.

    Instance Properties:

        elog -- r/w
    """

    def __init__(self, log=None):
        self._elog = []
        self.elog = log

    @property
    def elog(self):
        return self._elog

    @elog.setter
    def elog(self, value=''):
        if value is None:
            self._elog = []
        else:
            self._elog.append([CoreLog.date_stamper(), value])

    def __str__(self):
        return repr(self.elog)


class CoreLog:
    """A log object for the Core module.

    Logs errors and certain function/method calls/progress

    Functions:

        date_stamper

    Instance Properties:

        rlog -- r/w
        elog -- r/w
    """

    def __init__(self, rlog=None, elog=None):
        self._run_log = []
        self._error_log = []
        self.rlog = rlog
        self.elog = elog

    @property
    def rlog(self):
        return self._run_log

    @rlog.setter
    def rlog(self, value=''):
        if value is None:
            self._run_log = []
        else:
            self._run_log.append([CoreLog.date_stamper(), value])

    @rlog.deleter
    def rlog(self):
        pass

    @property
    def elog(self):
        return self._error_log

    @elog.setter
    def elog(self, value=''):
        if value is None:
            self._error_log = []
        else:
            self._error_log.append([CoreLog.date_stamper(), value])

    def elogger(self, value):
        for i in range(0, len(value)):
            self._error_log.append(value[i])

    def save_log(self):
        file = open('./session ' + CoreLog.date_stamper() + '.txt',
                    'w+')
        file.write('#####\nrun_log\n#####\n\n')
        for i in range(0, len(self.rlog)):
            file.write(str(self.rlog[i]))
            file.write('\n')

        file.write('\n#####\nerr_log\n#####\n\n')
        for i in range(0, len(self.elog)):
            file.write(str(self.elog[i]))
            file.write('\n')

        file.close()

    def __str__(self):
        return repr(self.elog)

    @staticmethod
    def date_stamper():
        return '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') \
               + ']'
