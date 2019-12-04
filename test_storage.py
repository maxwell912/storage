from progr_files.Storage import Storage


# python desktop\storage\progr_files\
class Test_storage:
    storage = None
    directory = ''
    open("directory", 'w').close()

    def test_init(self):
        Test_storage.storage = Storage(storage_dir=self.directory)
        assert Test_storage.storage

    def test_add(self):
        for i in range(100):
            Test_storage.storage.add(str(i), 'test' + str(i))

    def test_get(self):
        for i in range(100):
            s = Test_storage.storage.get(str(i))
            assert (s == 'test' + str(i))
        assert Test_storage.storage.get('s') is 'KeyError'

    def test_exist(self):
        assert Test_storage.storage.contains_key('1')
        assert not Test_storage.storage.contains_key('l')

    def test_delete(self):
        Test_storage.storage.remove_key('1')
        assert not Test_storage.storage.contains_key('1')
        Test_storage.storage.add('1', 'test1')

    def test_commit(self):
        Test_storage.storage._commit_dict()
        pass

    def test_recover(self):
        Test_storage.storage.add('a', 'testa')
        Test_storage.storage.remove_key('0')
        Test_storage.storage = Storage(storage_dir=self.directory)
        Test_storage.storage._retrieve_data()
        s = Test_storage.storage.get('a')
        assert (s == 'testa')
        assert not Test_storage.storage.contains_key('0')
        Test_storage.storage.add('0', 'test0')
        for i in range(100):
            s = Test_storage.storage.get(str(i))
            assert (s == 'test' + str(i))

    def test_get_saved_values(self):
        self.storage = Storage(self.directory)
        for i in range(100):
            s = Test_storage.storage.get(str(i))
            assert (s == 'test' + str(i))

    def test_defrag(self):
        Test_storage.storage._defrag()
