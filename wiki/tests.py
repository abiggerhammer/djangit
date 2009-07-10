#!/usr/bin/python
import unittest
import git
import copy
import pydjangitwiki.wiki.views
import pydjangitwiki.urls
#import django.test.client
import os #for rmall

def addfile(repo="",filename="myfilename",contents="contents",message="commit message"):
    if not repo: return False
    thefile = open(repo.git.get_dir + "/" + filename,"w")
    thefile.write(contents)
    thefile.close()
    repo.git.execute(["git","add",filename])
    repo.git.execute(["git","commit","-m",message])
    return True

def rmall(path="/tmp/some/dir/here/"):
    top = path
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
                os.remove(os.path.join(root, name))
        for name in dirs:
                os.rmdir(os.path.join(root, name))
    return

def begin(path="/tmp/tmprepo"):
    rmall(path)
    if git.os.path.exists(path): git.os.rmdir(path)
    git.os.mkdir(path)
    tmprepo = git.Repo.create(path,mkdir=True)
    tmprepo.git.execute(["git","init"])
    return tmprepo

def end(path="/tmp/tmprepo"):
    rmall(path)
    git.os.rmdir(path)
    return

def find_urls(methodname="index"):
    '''
    return all RegexURLPattern objects that call a certain method
    '''
    patterns = pydjangitwiki.urls.urlpatterns
    returnlist = []
    for pat in patterns:
        if pat.callback.__name__ == methodname:
            #see also: pat.callback.__module__
            returnlist.append(pat)
    return returnlist

def resolve(regexes=[],validpatterns=[]):
    returndict = {}
    for each in regexes:
        for pattern in validpatterns:
            if not each.resolve(pattern) == None:
                if not returndict.has_key(pattern):
                    returndict[pattern] = [each]
                else:
                    returndict[pattern].append(each)
    return returndict

class TestURLs(unittest.TestCase):
    def test_index(self):
        #pydjangitwiki.urls.urlpatterns that should return 'pydjangitwiki.wiki.views.index'
        #note: some of these patterns are handled by 'view' which then calls index()
        #validpatterns = ["/", "", "/folder-name/", "folder-name"]
        validpatterns = [""]
        regexes = find_urls(methodname="index")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_edit(self):
        validpatterns = [
                            "edit/",
                            "edit",
                            "home/something/something/edit",
                            "home/something/something/edit/",
                        ]
        regexes = find_urls(methodname="edit")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_archive(self):
        validpatterns = [
                            "archive/", #or is this a dir?
                            "archive",
                            "home/something/something/archive", #or is this a file?
                            "home/something/something/archive/", #or is this a dir?
                            "/archive", #or is this a file?
                            "/archive/", #or is this a dir?
                        ]
        regexes = find_urls(methodname="archive")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_history(self):
        validpatterns = [
                            "history",
                            "/history", #or is this a file?
                            "/history/", #or is this a dir?
                            "history/", #or is this a dir?
                            "some/path/here/history",
                            "some/path/here/history/", #or is this a dir?
                        ]
        regexes = find_urls(methodname="history")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_upload(self):
        validpatterns = [
                            "upload",
                            "some/path/to/a/file/upload",
                            #"some/path/to/a/dir/upload", #should this be invalid?
                        ]
        regexes = find_urls(methodname="upload")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_new(self):
        validpatterns = [
                            "new",
                            "some/path/to/a/dir/file/new",
                        ]
        regexes = find_urls(methodname="new")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_changelog(self):
        validpatterns = [
                            "changelog.rss",
                            "some/path/to/a/dir/file/changelog.rss",
                        ]
        regexes = find_urls(methodname="changelog")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_view(self):
        validpatterns = [
                            "some/path/to/a/file",
                            "some/path/to/a/dir/", #should redirect to index() however
                            "some/path/to/a/file/SHA_HERE",
                        ]
        regexes = find_urls(methodname="view")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_render(self):
        #not sure if we care about this hack of a function
        #it should be rewritten anyway
        pass

class TestViews(unittest.TestCase):
    def test_pop_path(self):
       path = "super/star/destroyer"
       self.assertTrue(pydjangitwiki.wiki.views.pop_path(path)=="star/destroyer")
       path ="/super/star/destroyer"
       #print pydjangitwiki.wiki.views.pop_path(path)
       self.assertTrue(pydjangitwiki.wiki.views.pop_path(path)=="star/destroyer")
       path = "one/two/three/four/"
       self.assertTrue(pydjangitwiki.wiki.views.pop_path(copy.copy(path))=="two/three/four/")
       popped = pydjangitwiki.wiki.views.pop_path(copy.copy(path))
       popped2 = pydjangitwiki.wiki.views.pop_path(copy.copy(popped))
       self.assertTrue(popped2=="three/four/")
    def test_children(self):
        #find all tree items and combine them into a dict
        #depth=-1 means infinite depth
        
        #make a repo, add files, commit, etc.
        #then check to see if those files are there
        #see git.Repo.init_bare(path,mkdir=True)
        #tmprepo = git.Repo.init_bare("/tmp/tmprepo/",mkdir=True)
        rmall("/tmp/tmprepo")
        if git.os.path.exists("/tmp/tmprepo"): git.os.rmdir("/tmp/tmprepo")
        git.os.mkdir("/tmp/tmprepo")
        tmprepo = git.Git("/tmp/tmprepo/")
        tmprepo.execute(["git","init"])
        somefile = open("/tmp/tmprepo/somefile","w")
        somefile.write("this is some file in the repository")
        somefile.close()
        fancyhat = open("/tmp/tmprepo/fancyhat","w")
        fancyhat.write("there is a fancy hat here")
        fancyhat.close()
        tmprepo.execute(["git","add","somefile"])
        tmprepo.execute(["git","add","fancyhat"])
        tmprepo.execute(["git","commit","-m","commited somefile and fancyhat"])

        children = pydjangitwiki.wiki.views.children(gitpath=tmprepo.get_dir)
        print "the children = ", children
        self.assertTrue(children.has_key("somefile"))
        self.assertTrue(children.has_key("fancyhat"))

        rmall(tmprepo.get_dir)
        git.os.rmdir(tmprepo.get_dir)

        #now make a repo, add files, commit, add folders, etc.
        #then check to see if those files & folders are there

        pass
    def test_find(self):
        pass
    def test_pathExists(self):
        tmprepo = begin(path="/tmp/tmprepo")
        addfile(repo=tmprepo,filename="superfile",contents="file contents, you see",message="added superfile")
        self.assertTrue(pydjangitwiki.wiki.views.pathExists(path="superfile",gitrepo=tmprepo))
        self.assertFalse(pydjangitwiki.wiki.views.pathExists(path="some_file_that_does_not_exist",gitrepo=tmprepo))
        end(tmprepo.git.get_dir)
        return
    def test_pathIsFile(self):
        tmprepo = begin(path="/tmp/tmprepo")
        print "test_pathIsFile says that tmprepo = ", tmprepo
        addfile(repo=tmprepo,filename="myfilename",contents="these are the contents of the file",message="added myfilename")
        self.assertTrue(pydjangitwiki.wiki.views.pathIsFile(path="myfilename",gitrepo=tmprepo))
        self.assertFalse(pydjangitwiki.wiki.views.pathIsFile(path="/",gitrepo=tmprepo))
        self.assertFalse(pydjangitwiki.wiki.views.pathIsFile(path="some_file_that_does_not_exist",gitrepo=tmprepo))
        end(tmprepo.git.get_dir)
        return
    def test_index(self):
        pass
    def test_edit(self):
        pass
    def test_archive(self):
        pass
    def test_history(self):
        pass
    def test_upload(self):
        pass
    def test_new(self):
        pass
    def test_changelog(self):
        pass
    def test_view(self):
        pass
    def test_render(self):
        #not sure if this needs to be tested
        #it's kind of a hack in the first place
        pass

if __name__ == '__main__':
    unittest.main()
