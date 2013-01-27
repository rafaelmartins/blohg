from pygit2 import Signature

def git_commit(repo, tree, files, parents=[]):
    for f in files:
        repo.index.add(f)
        entry = repo.index[f]
        tree.insert(f, entry.oid, 0o100644)
    repo.index.write()
    sign = Signature('foo', 'foo@example.com')
    return repo.create_commit('refs/heads/master', sign, sign, 'foo',
                              tree.write(), parents)
