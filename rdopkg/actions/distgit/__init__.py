from rdopkg.action import Action, Arg


ACTIONS = [
    Action('clone', atomic=True,
           help="clone an RDO package distgit and setup remotes",
           required_args=[
               Arg('package', positional=True, metavar='PACKAGE',
                   help="RDO package to clone (see `rdopkg info`)"),
           ],
           optional_args=[
               Arg('use_master_distgit', shortcut='-m', action='store_true',
                   help="clone 'master-distgit'"),
               Arg('gerrit_remotes', shortcut='-g', action='store_true',
                   help="create branches "
                        "'gerrit-origin' and 'gerrit-patches'"),
               Arg('review_user', shortcut='-u', metavar='USER',
                   help="gerrit username for reviews"),
           ]),
    Action('pkgenv', atomic=True, help="show detected package environment",
           steps=[
               Action('get_package_env'),
               Action('show_package_env'),
           ]),
    Action('patchlog', atomic=True, help="show patches branch log",
           steps=[
               Action('get_package_env'),
               Action('show_patch_log'),
           ]),
    Action('get-patches', atomic=True,
           help="setup local patches branch and switch to it",
           optional_args=[
               Arg('patches_branch', shortcut='-p', metavar='REMOTE/BRANCH',
                   help="remote git branch containing patches"),
               Arg('local_patches_branch', shortcut='-P',
                   metavar='LOCAL_BRANCH',
                   help="local git branch containing patches"),
               Arg('gerrit_patches_chain', shortcut='-g',
                   metavar='REVIEW_NUMBER',
                   help="top gerrit review id of the patch chain"),
               Arg('force', shortcut='-f', action='store_true',
                   help="use patch even if it was not validated in CI"),
           ],
           steps=[
               Action('get_package_env'),
               Action('ensure_patches_branch'),
               Action('get_patches_branch'),
               Action('checkout_patches_branch'),
           ]),
    Action('fix', help="change .spec file without introducing new patches",
           steps=[
               Action('get_package_env'),
               Action('update_spec'),
               Action('edit_spec'),
               Action('commit_distgit_update'),
               Action('final_spec_diff'),
           ]),
    Action('patch', atomic=True,
           help="introduce new patches to the package",
           optional_args=[
               Arg('patches_branch', shortcut='-p', metavar='REMOTE/BRANCH',
                   help="remote git branch containing patches"),
               Arg('local_patches_branch', shortcut='-P',
                   metavar='LOCAL_BRANCH',
                   help="local git branch containing patches"),
               Arg('local_patches', shortcut='-l', action='store_true',
                   help="don't reset local patches branch, use it as is"),
               Arg('gerrit_patches_chain', shortcut='-g',
                   metavar='REVIEW_NUMBER',
                   help="top gerrit review id of the patch chain"),
               Arg('force', shortcut='-f', action='store_true',
                   help="use patch even if it was not validated in CI"),
           ],
           steps=[
               Action('get_package_env'),
               Action('ensure_patches_branch'),
               Action('get_patches_branch'),
               Action('check_new_patches'),
               Action('update_patches',
                      const_args={'require_patches_change': True}),
               Action('update_spec'),
               Action('commit_distgit_update', const_args={'amend': True}),
               Action('final_spec_diff'),
           ]),
    Action('new_version', help="update package to new upstream version",
           optional_args=[
               Arg('new_version', positional=True, nargs='?',
                   help="version to update to"),
               Arg('patches_branch', shortcut='-p', metavar='REMOTE/BRANCH',
                   help="remote git branch containing patches"),
               Arg('local_patches_branch', shortcut='-P',
                   metavar='LOCAL_BRANCH',
                   help="local git branch containing patches"),
               Arg('local_patches', shortcut='-l', action='store_true',
                   help="don't reset local patches branch, use it as is"),
               Arg('bump_only', shortcut='-b', action='store_true',
                   help="only bump .spec to new version a la rpmdev-bumpspec"),
               Arg('no_diff', shortcut='-d', action='store_true',
                   help="don't show git/requirements diff"),
               Arg('new_sources', shortcut='-N', action='store_true',
                   help=("run `fedpkg new-sources`"
                         " (default: depends on branch name)")),
               Arg('no_new_sources', shortcut='-n', action='store_true',
                   help=("don't run `fedpkg new-sources`"
                         " (default: depends on branch name)")),
               Arg('unattended', shortcut='-U', action='store_true',
                   help="don't ask any questions (NOT RECOMMENDED)"),
               Arg('no_push_patches', shortcut='-t', action='store_true',
                   help="don't push patches branch"),
           ],
           steps=[
               Action('get_package_env'),
               Action('new_version_setup'),
               Action('diff'),
               Action('prep_new_patches_branch'),
               Action('get_patches_branch'),
               Action('rebase_patches_branch'),
               Action('update_spec'),
               Action('get_source'),
               Action('new_sources'),
               Action('commit_distgit_update'),
               Action('update_patches', const_args={'amend': True}),
               Action('final_spec_diff'),
               Action('review_patches_branch')
           ]),
    Action('update_patches', atomic=True,
           help="update patches from -patches branch",
           steps=[
               Action('get_package_env'),
               Action('update_patches'),
           ],
           optional_args=[
               Arg('amend', shortcut='-a', action='store_true',
                   help="amend previous commit"),
               Arg('local_patches_branch', shortcut='-P',
                   metavar='LOCAL_BRANCH',
                   help="local git branch containing patches"),
           ]),
    Action('amend', atomic=True,
           help="amend last commit and recreate commit message"),
    Action('squash', atomic=True,
           help="squash HEAD into HEAD~ using HEAD~ commit message"),
    Action('get_source', atomic=True, help="fetch source archive",
           steps=[
               Action('get_source', const_args={'new_sources': True})
           ]),
    Action('tag_patches', atomic=True,
           help='tag the -patches branch in Git with the current NVR',
           optional_args=[
               Arg('force', shortcut='-f', action='store_true',
                   help='replace an existing tag with this name'),
               Arg('push', shortcut='-p', action='store_true',
                   help='push this new tag to the patches remote'),
           ],
           steps=[
               Action('get_package_env'),
               Action('ensure_patches_branch'),
               Action('tag_patches_branch'),
           ]),
]
