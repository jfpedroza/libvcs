import pathlib
import shlex
from collections.abc import Sequence
from typing import Any, Literal, Optional, Union

from libvcs._internal.run import run
from libvcs._internal.types import StrOrBytesPath, StrPath

_CMD = Union[StrOrBytesPath, Sequence[StrOrBytesPath]]


class Git:
    def __init__(self, *, dir: StrPath) -> None:
        """Lite, typed, pythonic wrapper for git(1).

        Parameters
        ----------
        dir :
            Operates as PATH in the corresponding git subcommand.

        Examples
        --------
        >>> Git(dir=tmp_path)
        <Git dir=...>
        """
        #: Directory to check out
        self.dir: pathlib.Path
        if isinstance(dir, pathlib.Path):
            self.dir = dir
        else:
            self.dir = pathlib.Path(dir)

    def __repr__(self) -> str:
        return f"<Git dir={self.dir}>"

    def run(
        self,
        args: _CMD,
        *,
        # Print-and-exit flags
        version: Optional[bool] = None,
        help: Optional[bool] = None,
        html_path: Optional[bool] = None,
        man_path: Optional[bool] = None,
        info_path: Optional[bool] = None,
        # Normal flags
        C: Optional[Union[StrOrBytesPath, list[StrOrBytesPath]]] = None,
        cwd: Optional[StrOrBytesPath] = None,
        git_dir: Optional[StrOrBytesPath] = None,
        work_tree: Optional[StrOrBytesPath] = None,
        namespace: Optional[StrOrBytesPath] = None,
        super_prefix: Optional[StrOrBytesPath] = None,
        exec_path: Optional[StrOrBytesPath] = None,
        bare: Optional[bool] = None,
        no_replace_objects: Optional[bool] = None,
        literal_pathspecs: Optional[bool] = None,
        global_pathspecs: Optional[bool] = None,
        noglob_pathspecs: Optional[bool] = None,
        icase_pathspecs: Optional[bool] = None,
        no_optional_locks: Optional[bool] = None,
        config: Optional[str] = None,
        config_env: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Passing None to a subcommand option, the flag won't be passed unless otherwise
        stated.

        `git help` and `git help [cmd]`

        Wraps git's `Options <https://git-scm.com/docs/git#_options>`_.

        Parameters
        ----------
        cwd : :attr:`libvcs._internal.types.StrOrBytesPath`, optional, passed to
            subprocess's ``cwd`` the command runs from. Defaults to :attr:`~.cwd`.
        C : :attr:`libvcs._internal.types.StrOrBytesPath`, optional
            ``-C <path>``
        git_dir : :attr:`libvcs._internal.types.StrOrBytesPath`, optional
            ``--git-dir <path>``
        work_tree : :attr:`libvcs._internal.types.StrOrBytesPath`, optional
            ``--work-tree <path>``
        namespace : :attr:`libvcs._internal.types.StrOrBytesPath`, optional
            ``--namespace <path>``
        super_prefix : :attr:`libvcs._internal.types.StrOrBytesPath`, optional
            ``--super-prefix <path>``
        exec_path : :attr:`libvcs._internal.types.StrOrBytesPath`, optional
            ``--exec-path=<path>``
        bare : bool
            ``--bare``
        no_replace_objects : bool
            ``--no-replace-objects``
        literal_pathspecs : bool
            ``--literal-pathspecs``
        global_pathspecs : bool
            ``--glob-pathspecs``
        noglob_pathspecs : bool
            ``--noglob-pathspecs``
        icase_pathspecs : bool
            ``--icase-pathspecs``
        no_optional_locks : bool
            ``--no-optional-locks``
        version : bool
            ``--version``
        html_path : bool
            ``--html-path``
        man_path : bool
            ``--man-path``
        info_path : bool
            ``--info-path``
        help : bool
            ``-h / --help``
        pager : bool
            ``-p --pager``
        no_pager : bool
            ``-P / --no-pager``
        config :
            ``--config=<name>=<value>``
        config_env :
            ``--config-env=<name>=<envvar>``

        Examples
        --------
        >>> git = Git(dir=tmp_path)
        >>> git.run(['help'])
        "usage: git [...--version] [...--help] [-C <path>]..."
        """

        if isinstance(args, Sequence):
            cli_args = ["git", *args]
        else:
            cli_args = ["git", args]

        if "cwd" not in kwargs:
            kwargs["cwd"] = self.dir

        #
        # Print-and-exit
        #
        if version is True:
            cli_args.append("--version")
        if help is True:
            cli_args.append("--help")
        if html_path is True:
            cli_args.append("--html-path")
        if man_path is True:
            cli_args.append("--man-path")
        if info_path is True:
            cli_args.append("--info-path")

        #
        # Flags
        #
        if C is not None:
            if not isinstance(C, list):
                C = [C]
            C = [str(c) for c in C]
            cli_args.extend(["-C", C])
        if git_dir is not None:
            cli_args.extend(["--git-dir", str(git_dir)])
        if work_tree is not None:
            cli_args.extend(["--work-tree", str(work_tree)])
        if namespace is not None:
            cli_args.extend(["--namespace", namespace])
        if super_prefix is not None:
            cli_args.extend(["--super-prefix", super_prefix])
        if exec_path is not None:
            cli_args.extend(["--exec-path", exec_path])
        if bare is True:
            cli_args.append("--bare")
        if no_replace_objects is True:
            cli_args.append("--no-replace-objects")
        if literal_pathspecs is True:
            cli_args.append("--literal-pathspecs")
        if global_pathspecs is True:
            cli_args.append("--global-pathspecs")
        if noglob_pathspecs is True:
            cli_args.append("--noglob-pathspecs")
        if icase_pathspecs is True:
            cli_args.append("--icase-pathspecs")
        if no_optional_locks is True:
            cli_args.append("--no-optional-locks")

        return run(args=cli_args, **kwargs)

    def clone(
        self,
        *,
        url: str,
        separate_git_dir: Optional[StrOrBytesPath] = None,
        template: Optional[str] = None,
        depth: Optional[str] = None,
        branch: Optional[str] = None,
        origin: Optional[str] = None,
        upload_pack: Optional[str] = None,
        shallow_since: Optional[str] = None,
        shallow_exclude: Optional[str] = None,
        reference: Optional[str] = None,
        reference_if_able: Optional[str] = None,
        server_option: Optional[str] = None,
        jobs: Optional[str] = None,
        force: Optional[bool] = None,
        local: Optional[bool] = None,
        all: Optional[bool] = None,
        no_hardlinks: Optional[bool] = None,
        hardlinks: Optional[bool] = None,
        shared: Optional[bool] = None,
        progress: Optional[bool] = None,
        no_checkout: Optional[bool] = None,
        no_reject_shallow: Optional[bool] = None,
        reject_shallow: Optional[bool] = None,
        sparse: Optional[bool] = None,
        shallow_submodules: Optional[bool] = None,
        no_shallow_submodules: Optional[bool] = None,
        remote_submodules: Optional[bool] = None,
        no_remote_submodules: Optional[bool] = None,
        verbose: Optional[bool] = None,
        quiet: Optional[bool] = None,
        # Special behavior
        make_parents: Optional[bool] = True,
        **kwargs: Any,
    ) -> str:
        """Clone a working copy from an git repo.

        Wraps `git clone <https://git-scm.com/docs/git-clone>`_.

        Parameters
        ----------
        url : str
        directory : str
        separate_git_dir : StrOrBytesPath
            Separate repository (.git/ ) from working tree
        force : bool, optional
            force operation to run
        make_parents : bool, default: ``True``
            Creates checkout directory (`:attr:`self.dir`) if it doesn't already exist.

        Examples
        --------
        >>> git = Git(dir=tmp_path)
        >>> git_remote_repo = create_git_remote_repo()
        >>> git.clone(url=f'file://{git_remote_repo}')
        ''
        >>> git.dir.exists()
        True
        """
        required_flags: list[str] = [url, str(self.dir)]
        local_flags: list[str] = []

        if template is not None:
            local_flags.append(f"--template={template}")
        if separate_git_dir is not None:
            local_flags.append(f"--separate-git-dir={separate_git_dir!r}")
        if (filter := kwargs.pop("filter", None)) is not None:
            local_flags.append(f"--filter={filter}")
        if depth is not None:
            local_flags.extend(["--depth", depth])
        if branch is not None:
            local_flags.extend(["--branch", branch])
        if origin is not None:
            local_flags.extend(["--origin", origin])
        if upload_pack is not None:
            local_flags.extend(["--upload-pack", upload_pack])
        if shallow_since is not None:
            local_flags.append(f"--shallow-since={shallow_since}")
        if shallow_exclude is not None:
            local_flags.append(f"--shallow-exclude={shallow_exclude}")
        if reference is not None:
            local_flags.extend(["--reference", reference])
        if reference_if_able is not None:
            local_flags.extend(["--reference", reference_if_able])
        if server_option is not None:
            local_flags.append(f"--server-option={server_option}")
        if jobs is not None:
            local_flags.extend(["--jobs", jobs])
        if local is True:
            local_flags.append("--local")
        if hardlinks is True:
            local_flags.append("--hardlinks")
        if no_hardlinks is True:
            local_flags.append("--no-hardlinks")
        if shared is True:
            local_flags.append("--shared")
        if quiet is True:
            local_flags.append("--quiet")
        if verbose is True:
            local_flags.append("--verbose")
        if progress is True:
            local_flags.append("--progress")
        if no_checkout is True:
            local_flags.append("--no-checkout")
        if no_reject_shallow is True:
            local_flags.append("--no-reject-shallow")
        if reject_shallow is True:
            local_flags.append("--reject-shallow")
        if sparse is True:
            local_flags.append("--sparse")
        if shallow_submodules is True:
            local_flags.append("--shallow-submodules")
        if no_shallow_submodules is True:
            local_flags.append("--no-shallow-submodules")
        if remote_submodules is True:
            local_flags.append("--remote-submodules")
        if no_remote_submodules is True:
            local_flags.append("--no-remote-submodules")

        # libvcs special behavior
        if make_parents and not self.dir.exists():
            self.dir.mkdir(parents=True)
        return self.run(
            ["clone", *local_flags, "--", *required_flags], check_returncode=False
        )

    def fetch(
        self,
        *,
        reftag: Optional[Any] = None,
        deepen: Optional[str] = None,
        depth: Optional[str] = None,
        branch: Optional[str] = None,
        origin: Optional[str] = None,
        upload_pack: Optional[str] = None,
        shallow_since: Optional[str] = None,
        shallow_exclude: Optional[str] = None,
        negotiation_tip: Optional[str] = None,
        jobs: Optional[str] = None,
        server_option: Optional[str] = None,
        recurse_submodules: Optional[
            Union[bool, Literal["yes", "on-demand", "no"]]
        ] = None,
        recurse_submodules_default: Optional[
            Union[bool, Literal["yes", "on-demand"]]
        ] = None,
        submodule_prefix: Optional[StrOrBytesPath] = None,
        #
        all: Optional[bool] = None,
        force: Optional[bool] = None,
        keep: Optional[bool] = None,
        multiple: Optional[bool] = None,
        dry_run: Optional[bool] = None,
        append: Optional[bool] = None,
        atomic: Optional[bool] = None,
        ipv4: Optional[bool] = None,
        ipv6: Optional[bool] = None,
        progress: Optional[bool] = None,
        quiet: Optional[bool] = None,
        verbose: Optional[bool] = None,
        unshallow: Optional[bool] = None,
        update_shallow: Optional[bool] = None,
        negotiate_tip: Optional[bool] = None,
        no_write_fetch_head: Optional[bool] = None,
        write_fetch_head: Optional[bool] = None,
        no_auto_maintenance: Optional[bool] = None,
        auto_maintenance: Optional[bool] = None,
        no_write_commit_graph: Optional[bool] = None,
        write_commit_graph: Optional[bool] = None,
        prefetch: Optional[bool] = None,
        prune: Optional[bool] = None,
        prune_tags: Optional[bool] = None,
        no_tags: Optional[bool] = None,
        tags: Optional[bool] = None,
        no_recurse_submodules: Optional[bool] = None,
        set_upstream: Optional[bool] = None,
        update_head_ok: Optional[bool] = None,
        show_forced_updates: Optional[bool] = None,
        no_show_forced_updates: Optional[bool] = None,
        negotiate_only: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """Download from repo. Wraps `git fetch <https://git-scm.com/docs/git-fetch>`_.

        Examples
        --------
        >>> git = Git(dir=git_local_clone.dir)
        >>> git_remote_repo = create_git_remote_repo()
        >>> git.fetch()
        ''
        >>> git = Git(dir=git_local_clone.dir)
        >>> git_remote_repo = create_git_remote_repo()
        >>> git.fetch(reftag=f'file://{git_remote_repo}')
        ''
        >>> git.dir.exists()
        True
        """
        required_flags: list[str] = []
        if reftag:
            required_flags.insert(0, reftag)
        local_flags: list[str] = []

        if submodule_prefix is not None:
            local_flags.append(f"--submodule-prefix={submodule_prefix!r}")
        if (filter := kwargs.pop("filter", None)) is not None:
            local_flags.append(f"--filter={filter}")
        if depth is not None:
            local_flags.extend(["--depth", depth])
        if branch is not None:
            local_flags.extend(["--branch", branch])
        if origin is not None:
            local_flags.extend(["--origin", origin])
        if upload_pack is not None:
            local_flags.extend(["--upload-pack", upload_pack])
        if shallow_since is not None:
            local_flags.append(f"--shallow-since={shallow_since}")
        if shallow_exclude is not None:
            local_flags.append(f"--shallow-exclude={shallow_exclude}")
        if server_option is not None:
            local_flags.append(f"--server-option={server_option}")
        if jobs is not None:
            local_flags.extend(["--jobs", jobs])
        if keep:
            local_flags.append("--keep")
        if force:
            local_flags.append("--force")
        if multiple:
            local_flags.append("--multiple")
        if quiet:
            local_flags.append("--quiet")
        if progress:
            local_flags.append("--progress")
        if verbose:
            local_flags.append("--verbose")
        if all:
            local_flags.append("--all")
        if atomic:
            local_flags.append("--atomic")
        if unshallow:
            local_flags.append("--unshallow")
        if append:
            local_flags.append("--append")
        if update_shallow:
            local_flags.append("--update-shallow")
        if dry_run:
            local_flags.append("--dry-run")
        if no_write_fetch_head:
            local_flags.append("--no-write-fetch-head")
        if write_fetch_head:
            local_flags.append("--write-fetch-head")
        if auto_maintenance:
            local_flags.append("--auto-maintenance")
        if no_auto_maintenance:
            local_flags.append("--no-auto-maintenance")
        if write_commit_graph:
            local_flags.append("--write-commit-graph")
        if no_write_commit_graph:
            local_flags.append("--no-write-commit-graph")
        if prefetch:
            local_flags.append("--prefetch")
        if prune:
            local_flags.append("--prune")
        if prune_tags:
            local_flags.append("--prune-tags")
        if tags:
            local_flags.append("--tags")
        if no_tags:
            local_flags.append("--no-tags")
        if no_recurse_submodules:
            local_flags.append("--no-recurse-submodules")
        if set_upstream:
            local_flags.append("--set-upstream")
        if update_head_ok:
            local_flags.append("--update-head-ok")
        if show_forced_updates:
            local_flags.append("--show-forced-updates")
        if no_show_forced_updates:
            local_flags.append("--no-show-forced-updates")
        if negotiate_only:
            local_flags.append("--negotiate-only")
        return self.run(
            ["fetch", *local_flags, "--", *required_flags], check_returncode=False
        )

    def rebase(
        self,
        *,
        upstream: Optional[str] = None,
        onto: Optional[str] = None,
        branch: Optional[str] = None,
        apply: Optional[bool] = None,
        merge: Optional[bool] = None,
        quiet: Optional[bool] = None,
        verbose: Optional[bool] = None,
        stat: Optional[bool] = None,
        no_stat: Optional[bool] = None,
        verify: Optional[bool] = None,
        no_verify: Optional[bool] = None,
        fork_point: Optional[bool] = None,
        no_fork_point: Optional[bool] = None,
        whitespace: Optional[str] = None,
        no_whitespace: Optional[bool] = None,
        commit_date_is_author_date: Optional[bool] = None,
        ignore_date: Optional[bool] = None,
        root: Optional[bool] = None,
        autostash: Optional[bool] = None,
        no_autostash: Optional[bool] = None,
        autosquash: Optional[bool] = None,
        no_autosquash: Optional[bool] = None,
        reschedule_failed_exec: Optional[bool] = None,
        no_reschedule_failed_exec: Optional[bool] = None,
        context: Optional[int] = None,
        rerere_autoupdate: Optional[bool] = None,
        no_rerere_autoupdate: Optional[bool] = None,
        keep_empty: Optional[bool] = None,
        no_keep_empty: Optional[bool] = None,
        reapply_cherry_picks: Optional[bool] = None,
        no_reapply_cherry_picks: Optional[bool] = None,
        allow_empty_message: Optional[bool] = None,
        signoff: Optional[bool] = None,
        keep_base: Optional[bool] = None,
        strategy: Optional[Union[str, bool]] = None,
        strategy_option: Optional[str] = None,
        exec: Optional[str] = None,
        gpg_sign: Optional[Union[str, bool]] = None,
        no_gpg_sign: Optional[bool] = None,
        empty: Optional[Union[str, Literal["drop", "keep", "ask"]]] = None,
        rebase_merges: Optional[
            Union[str, Literal["rebase-cousins", "no-rebase-cousins"]]
        ] = None,
        #
        # Interactive
        #
        interactive: Optional[bool] = None,
        edit_todo: Optional[bool] = None,
        skip: Optional[bool] = None,
        show_current_patch: Optional[bool] = None,
        abort: Optional[bool] = None,
        quit: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """Reapply commit on top of another tip.

        Wraps `git rebase <https://git-scm.com/docs/git-rebase>`_.

        Parameters
        ----------
        continue : bool
            Accepted via kwargs

        Examples
        --------
        >>> git = Git(dir=git_local_clone.dir)
        >>> git_remote_repo = create_git_remote_repo()
        >>> git.rebase()
        'Current branch master is up to date.'

        Declare upstream:

        >>> git = Git(dir=git_local_clone.dir)
        >>> git_remote_repo = create_git_remote_repo()
        >>> git.rebase(upstream='origin')
        'Current branch master is up to date.'
        >>> git.dir.exists()
        True
        """
        required_flags: list[str] = []
        local_flags: list[str] = []

        if upstream:
            required_flags.insert(0, upstream)
        if branch:
            required_flags.insert(0, branch)
        if onto:
            local_flags.extend(["--onto", onto])
        if context:
            local_flags.extend(["--C", str(context)])

        if exec:
            local_flags.extend(["--exec", shlex.quote(exec)])
        if reschedule_failed_exec:
            local_flags.append("--reschedule-failed-exec")
        if no_reschedule_failed_exec:
            local_flags.append("--no-reschedule-failed-exec")
        if fork_point:
            local_flags.append("--fork-point")
        if no_fork_point:
            local_flags.append("--no-fork-point")
        if root:
            local_flags.append("--root")
        if keep_base:
            local_flags.append("--keep-base")
        if autostash:
            local_flags.append("--autostash")
        if no_autostash:
            local_flags.append("--no-autostash")

        if merge:
            local_flags.append("--merge")

        if verbose:
            local_flags.append("--verbose")
        if quiet:
            local_flags.append("--quiet")
        if stat:
            local_flags.append("--stat")
        if no_stat:
            local_flags.append("--no-stat")

        if whitespace:
            local_flags.append("--whitespace")
        if no_whitespace:
            local_flags.append("--no-whitespace")

        if rerere_autoupdate:
            local_flags.append("--rerere-autoupdate")
        if no_rerere_autoupdate:
            local_flags.append("--no-rerwre-autoupdate")

        if reapply_cherry_picks:
            local_flags.append("--reapply-cherry-picks")
        if no_reapply_cherry_picks:
            local_flags.append("--no-reapply-cherry-picks")

        if keep_empty:
            local_flags.append("--keep-empty")
        if no_keep_empty:
            local_flags.append("--no-keep-empty")

        if verify:
            local_flags.append("--verify")
        if no_verify:
            local_flags.append("--no-verify")

        if ignore_date:
            local_flags.append("--ignore-date")
        if commit_date_is_author_date:
            local_flags.append("--commit-date-is-author-date")

        if empty is not None:
            if isinstance(empty, str):
                local_flags.append(f"--empty={empty}")
            else:
                local_flags.append("--empty")

        if rebase_merges is not None:
            if isinstance(rebase_merges, str):
                local_flags.append(f"--rebase-merges={rebase_merges}")
            else:
                local_flags.append("--rebase-merges")

        if gpg_sign is not None:
            if isinstance(gpg_sign, str):
                local_flags.append(f"--gpg-sign={gpg_sign}")
            else:
                local_flags.append("--gpg-sign")
        if no_gpg_sign:
            local_flags.append("--no-gpg-sign")
        if signoff:
            local_flags.append("--signoff")

        #
        # Interactive
        #
        if interactive:
            local_flags.append("--interactive")
        if kwargs.get("continue"):
            local_flags.append("--continue")
        if abort:
            local_flags.append("--abort")
        if edit_todo:
            local_flags.append("--edit-todo")
        if show_current_patch:
            local_flags.append("--show-current-patch")
        if quit:
            local_flags.append("--quit")

        return self.run(
            ["rebase", *local_flags, *required_flags], check_returncode=False
        )

    def pull(
        self,
        *,
        reftag: Optional[Any] = None,
        repository: Optional[str] = None,
        deepen: Optional[str] = None,
        depth: Optional[str] = None,
        branch: Optional[str] = None,
        origin: Optional[str] = None,
        upload_pack: Optional[str] = None,
        shallow_since: Optional[str] = None,
        shallow_exclude: Optional[str] = None,
        negotiation_tip: Optional[str] = None,
        jobs: Optional[str] = None,
        server_option: Optional[str] = None,
        recurse_submodules: Optional[
            Union[bool, Literal["yes", "on-demand", "no"]]
        ] = None,
        recurse_submodules_default: Optional[
            Union[bool, Literal["yes", "on-demand"]]
        ] = None,
        submodule_prefix: Optional[StrOrBytesPath] = None,
        #
        # Pull specific flags
        #
        # Options related to git pull
        # https://git-scm.com/docs/git-pull#_options_related_to_pull
        #
        cleanup: Optional[str] = None,
        rebase: Optional[Union[str, bool]] = None,
        no_rebase: Optional[bool] = None,
        strategy: Optional[Union[str, bool]] = None,
        strategy_option: Optional[str] = None,
        gpg_sign: Optional[Union[str, bool]] = None,
        no_gpg_sign: Optional[bool] = None,
        commit: Optional[bool] = None,
        no_commit: Optional[bool] = None,
        edit: Optional[bool] = None,
        no_edit: Optional[bool] = None,
        fast_forward_only: Optional[bool] = None,
        fast_forward: Optional[bool] = None,
        no_fast_forward: Optional[bool] = None,
        sign_off: Optional[bool] = None,
        no_sign_off: Optional[bool] = None,
        stat: Optional[bool] = None,
        no_stat: Optional[bool] = None,
        squash: Optional[bool] = None,
        no_squash: Optional[bool] = None,
        verify: Optional[bool] = None,
        no_verify: Optional[bool] = None,
        verify_signatures: Optional[bool] = None,
        no_verify_signatures: Optional[bool] = None,
        summary: Optional[bool] = None,
        no_summary: Optional[bool] = None,
        autostash: Optional[bool] = None,
        no_autostash: Optional[bool] = None,
        allow_unrelated_histories: Optional[bool] = None,
        #
        # Options related to git fetch
        # https://git-scm.com/docs/git-pull#_options_related_to_fetching
        #
        fetch: Optional[bool] = None,
        no_fetch: Optional[bool] = None,
        all: Optional[bool] = None,
        force: Optional[bool] = None,
        keep: Optional[bool] = None,
        multiple: Optional[bool] = None,
        dry_run: Optional[bool] = None,
        append: Optional[bool] = None,
        atomic: Optional[bool] = None,
        ipv4: Optional[bool] = None,
        ipv6: Optional[bool] = None,
        progress: Optional[bool] = None,
        quiet: Optional[bool] = None,
        verbose: Optional[bool] = None,
        unshallow: Optional[bool] = None,
        update_shallow: Optional[bool] = None,
        negotiate_tip: Optional[bool] = None,
        no_write_fetch_head: Optional[bool] = None,
        write_fetch_head: Optional[bool] = None,
        no_auto_maintenance: Optional[bool] = None,
        auto_maintenance: Optional[bool] = None,
        no_write_commit_graph: Optional[bool] = None,
        write_commit_graph: Optional[bool] = None,
        prefetch: Optional[bool] = None,
        prune: Optional[bool] = None,
        prune_tags: Optional[bool] = None,
        no_tags: Optional[bool] = None,
        tags: Optional[bool] = None,
        no_recurse_submodules: Optional[bool] = None,
        set_upstream: Optional[bool] = None,
        update_head_ok: Optional[bool] = None,
        show_forced_updates: Optional[bool] = None,
        no_show_forced_updates: Optional[bool] = None,
        negotiate_only: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """Download from repo. Wraps `git pull <https://git-scm.com/docs/git-pull>`_.

        Examples
        --------
        >>> git = Git(dir=git_local_clone.dir)
        >>> git_remote_repo = create_git_remote_repo()
        >>> git.pull()
        'Already up to date.'

        Fetch via ref:

        >>> git = Git(dir=tmp_path)
        >>> git.run(['init'])
        'Initialized ...'
        >>> git_remote_repo = create_git_remote_repo()
        >>> git.pull(reftag=f'file://{git_remote_repo}')
        ''
        >>> git.dir.exists()
        True
        """
        required_flags: list[str] = []
        if repository:
            required_flags.insert(0, repository)
        if reftag:
            required_flags.insert(0, reftag)
        local_flags: list[str] = []

        #
        # Pull-related arguments
        #
        if rebase is not None:
            if isinstance(rebase, str):
                local_flags.append(f"--rebase={rebase}")
            else:
                local_flags.append("--rebase")
        if no_rebase:
            local_flags.append("--no-rebase")
        if strategy is not None:
            if isinstance(strategy, str):
                local_flags.append(f"--strategy={strategy}")
            else:
                local_flags.append("--strategy")
        if strategy_option is not None:
            local_flags.append(f"--strategy-option={strategy_option}")
        if gpg_sign is not None:
            if isinstance(gpg_sign, str):
                local_flags.append(f"--gpg-sign={gpg_sign}")
            else:
                local_flags.append("--gpg-sign")
        if no_gpg_sign:
            local_flags.append("--no-gpg-sign")
        if cleanup:
            local_flags.append("--cleanup")
        if commit:
            local_flags.append("--commit")
        if no_commit:
            local_flags.append("--no-commit")
        if fast_forward:
            local_flags.append("--fast-forward")
        if fast_forward_only:
            local_flags.append("--fast-forward-only")
        if no_fast_forward:
            local_flags.append("--no-fast-forward")
        if edit:
            local_flags.append("--edit")
        if no_edit:
            local_flags.append("--no-edit")
        if sign_off:
            local_flags.append("--sign_off")
        if no_sign_off:
            local_flags.append("--no-sign_off")
        if stat:
            local_flags.append("--stat")
        if no_stat:
            local_flags.append("--no-stat")
        if squash:
            local_flags.append("--squash")
        if no_squash:
            local_flags.append("--no-squash")
        if verify:
            local_flags.append("--verify")
        if no_verify:
            local_flags.append("--no-verify")
        if verify_signatures:
            local_flags.append("--verify-signatures")
        if no_verify_signatures:
            local_flags.append("--no-verify-signatures")
        if summary:
            local_flags.append("--summary")
        if no_summary:
            local_flags.append("--no-summary")
        if autostash:
            local_flags.append("--autostash")
        if no_autostash:
            local_flags.append("--no-autostash")
        if allow_unrelated_histories:
            local_flags.append("--allow-unrelated-histories")
        #
        # Fetch-related arguments
        #
        if submodule_prefix is not None:
            local_flags.append(f"--submodule-prefix={submodule_prefix!r}")
        if (filter := kwargs.pop("filter", None)) is not None:
            local_flags.append(f"--filter={filter}")
        if depth is not None:
            local_flags.extend(["--depth", depth])
        if branch is not None:
            local_flags.extend(["--branch", branch])
        if origin is not None:
            local_flags.extend(["--origin", origin])
        if upload_pack is not None:
            local_flags.extend(["--upload-pack", upload_pack])
        if shallow_since is not None:
            local_flags.append(f"--shallow-since={shallow_since}")
        if shallow_exclude is not None:
            local_flags.append(f"--shallow-exclude={shallow_exclude}")
        if server_option is not None:
            local_flags.append(f"--server-option={server_option}")
        if jobs is not None:
            local_flags.extend(["--jobs", jobs])
        if keep:
            local_flags.append("--keep")
        if force:
            local_flags.append("--force")
        if multiple:
            local_flags.append("--multiple")
        if quiet:
            local_flags.append("--quiet")
        if progress:
            local_flags.append("--progress")
        if verbose:
            local_flags.append("--verbose")
        if all:
            local_flags.append("--all")
        if atomic:
            local_flags.append("--atomic")
        if unshallow:
            local_flags.append("--unshallow")
        if append:
            local_flags.append("--append")
        if update_shallow:
            local_flags.append("--update-shallow")
        if dry_run:
            local_flags.append("--dry-run")
        if no_write_fetch_head:
            local_flags.append("--no-write-fetch-head")
        if write_fetch_head:
            local_flags.append("--write-fetch-head")
        if auto_maintenance:
            local_flags.append("--auto-maintenance")
        if no_auto_maintenance:
            local_flags.append("--no-auto-maintenance")
        if write_commit_graph:
            local_flags.append("--write-commit-graph")
        if no_write_commit_graph:
            local_flags.append("--no-write-commit-graph")
        if prefetch:
            local_flags.append("--prefetch")
        if prune:
            local_flags.append("--prune")
        if prune_tags:
            local_flags.append("--prune-tags")
        if tags:
            local_flags.append("--tags")
        if no_tags:
            local_flags.append("--no-tags")
        if no_recurse_submodules:
            local_flags.append("--no-recurse-submodules")
        if set_upstream:
            local_flags.append("--set-upstream")
        if update_head_ok:
            local_flags.append("--update-head-ok")
        if show_forced_updates:
            local_flags.append("--show-forced-updates")
        if no_show_forced_updates:
            local_flags.append("--no-show-forced-updates")
        if negotiate_only:
            local_flags.append("--negotiate-only")
        return self.run(
            ["pull", *local_flags, "--", *required_flags], check_returncode=False
        )

    def init(
        self,
        *,
        template: Optional[str] = None,
        separate_git_dir: Optional[StrOrBytesPath] = None,
        object_format: Optional[Literal["sha1", "sha256"]] = None,
        branch: Optional[str] = None,
        initial_branch: Optional[str] = None,
        shared: Optional[bool] = None,
        quiet: Optional[bool] = None,
        bare: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """Create empty repo. Wraps `git init <https://git-scm.com/docs/git-init>`_.

        Parameters
        ----------
        quiet : bool
            ``--quiet``
        bare : bool
            ``--bare``
        object_format :
            Hash algorithm used for objects. SHA-256 is still experimental as of git
            2.36.0.

        Examples
        --------
        >>> new_repo = tmp_path / 'example'
        >>> new_repo.mkdir()
        >>> git = Git(dir=new_repo)
        >>> git.init()
        'Initialized empty Git repository in ...'
        >>> pathlib.Path(new_repo / 'test').write_text('foo', 'utf-8')
        3
        >>> git.run(['add', '.'])
        ''

        Bare:

        >>> new_repo = tmp_path / 'example1'
        >>> new_repo.mkdir()
        >>> git = Git(dir=new_repo)
        >>> git.init(bare=True)
        'Initialized empty Git repository in ...'
        >>> pathlib.Path(new_repo / 'HEAD').exists()
        True

        Existing repo:

        >>> git = Git(dir=new_repo)
        >>> git = Git(dir=git_local_clone.dir)
        >>> git_remote_repo = create_git_remote_repo()
        >>> git.init()
        'Reinitialized existing Git repository in ...'

        """
        required_flags: list[str] = [str(self.dir)]
        local_flags: list[str] = []

        if template is not None:
            local_flags.append(f"--template={template}")
        if separate_git_dir is not None:
            local_flags.append(f"--separate-git-dir={separate_git_dir!r}")
        if object_format is not None:
            local_flags.append(f"--object-format={object_format}")
        if branch is not None:
            local_flags.extend(["--branch", branch])
        if initial_branch is not None:
            local_flags.extend(["--initial-branch", initial_branch])
        if shared is True:
            local_flags.append("--shared")
        if quiet is True:
            local_flags.append("--quiet")
        if bare is True:
            local_flags.append("--bare")

        return self.run(
            ["init", *local_flags, "--", *required_flags], check_returncode=False
        )

    def help(
        self,
        *,
        all: Optional[bool] = None,
        verbose: Optional[bool] = None,
        no_external_commands: Optional[bool] = None,
        no_aliases: Optional[bool] = None,
        config: Optional[bool] = None,
        guides: Optional[bool] = None,
        info: Optional[bool] = None,
        man: Optional[bool] = None,
        web: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """Help info. Wraps `git help <https://git-scm.com/docs/git-help>`_.

        Parameters
        ----------
        all : bool
            Prints everything.

        no_external_commands : bool
            For use with ``all``, excludes external commands.

        no_aliases : bool
            For use with ``all``, excludes aliases.

        verbose : bool
            For us with ``all``, on by default.

        config : bool
            List all config vars.

        guides : bool
            List concept guides.

        info : bool
            Display man page in info format.

        man : bool
            Man page.

        web : bool
            Man page in HTML.

        Examples
        --------
        >>> git = Git(dir=tmp_path)

        >>> git.help()
        "usage: git [...--version] [...--help] [-C <path>]..."

        >>> git.help(all=True)
        "See 'git help <command>' to read about a specific subcommand..."

        >>> git.help(info=True)
        "usage: git [...--version] [...--help] [-C <path>] [-c <name>=<value>]..."

        >>> git.help(man=True)
        "usage: git [...--version] [...--help] [-C <path>] [-c <name>=<value>]..."
        """
        local_flags: list[str] = []

        if verbose is True:
            local_flags.append("--verbose")
        if all is True:
            local_flags.append("--all")
        if no_external_commands is True:
            local_flags.append("--no-external-commands")
        if no_aliases is True:
            local_flags.append("--no-aliases")
        if config is True:
            local_flags.append("--config")
        if guides is True:
            local_flags.append("--guides")
        if info is True:
            local_flags.append("--info")
        if man is True:
            local_flags.append("--man")
        if web is True:
            local_flags.append("--web")

        return self.run(["help", *local_flags], check_returncode=False)

    def reset(
        self,
        *,
        quiet: Optional[bool] = None,
        refresh: Optional[bool] = None,
        no_refresh: Optional[bool] = None,
        pathspec_from_file: Optional[StrOrBytesPath] = None,
        pathspec: Optional[Union[StrOrBytesPath, list[StrOrBytesPath]]] = None,
        soft: Optional[bool] = None,
        mixed: Optional[bool] = None,
        hard: Optional[bool] = None,
        merge: Optional[bool] = None,
        keep: Optional[bool] = None,
        commit: Optional[str] = None,
        recurse_submodules: Optional[bool] = None,
        no_recurse_submodules: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """Reset HEAD. Wraps `git help <https://git-scm.com/docs/git-help>`_.

        Parameters
        ----------
        quiet : bool
        no_refresh : bool
        refresh : bool
        pathspec_from_file : :attr:`libvcs._internal.types.StrOrBytesPath`
        pathspec_file_nul : bool
        pathspec : :attr:`libvcs._internal.types.StrOrBytesPath` or list
            :attr:`libvcs._internal.types.StrOrBytesPath`
        soft : bool
        mixed : bool
        hard : bool
        merge : bool
        keep : bool
        commit : str

        Examples
        --------
        >>> git = Git(dir=git_local_clone.dir)

        >>> git.reset()
        ''

        >>> git.reset(soft=True, commit='HEAD~0')
        ''
        """
        local_flags: list[str] = []

        if quiet is True:
            local_flags.append("--quiet")
        if no_refresh is True:
            local_flags.append("--no-refresh")
        if refresh is True:
            local_flags.append("--refresh")
        if pathspec_from_file is not None:
            local_flags.append(f"--pathspec_from_file={pathspec_from_file!r}")

        # HEAD to commit form
        if soft is True:
            local_flags.append("--soft")

        if mixed is True:
            local_flags.append("--mixed")

        if hard is True:
            local_flags.append("--hard")

        if merge is True:
            local_flags.append("--merge")

        if keep is True:
            local_flags.append("--keep")

        if commit is not None:
            local_flags.append(commit)

        if recurse_submodules:
            local_flags.append("--recurse-submodules")
        elif no_recurse_submodules:
            local_flags.append("--no-recurse-submodules")

        if pathspec is not None:
            if not isinstance(pathspec, list):
                pathspec = [pathspec]
        else:
            pathspec = []

        return self.run(
            ["reset", *local_flags, *(["--", *pathspec] if len(pathspec) else [])],
            check_returncode=False,
        )

    def checkout(
        self,
        *,
        quiet: Optional[bool] = None,
        progress: Optional[bool] = None,
        no_progress: Optional[bool] = None,
        pathspec_from_file: Optional[StrOrBytesPath] = None,
        pathspec: Optional[Union[StrOrBytesPath, list[StrOrBytesPath]]] = None,
        force: Optional[bool] = None,
        ours: Optional[bool] = None,
        theirs: Optional[bool] = None,
        no_track: Optional[bool] = None,
        guess: Optional[bool] = None,
        no_guess: Optional[bool] = None,
        _list: Optional[bool] = None,
        detach: Optional[bool] = None,
        merge: Optional[bool] = None,
        ignore_skip_worktree_bits: Optional[bool] = None,
        patch: Optional[bool] = None,
        orphan: Optional[str] = None,
        conflict: Optional[str] = None,
        overwrite_ignore: Optional[bool] = None,
        no_overwrite_ignore: Optional[bool] = None,
        recurse_submodules: Optional[bool] = None,
        no_recurse_submodules: Optional[bool] = None,
        overlay: Optional[bool] = None,
        no_overlay: Optional[bool] = None,
        commit: Optional[str] = None,
        branch: Optional[str] = None,
        new_branch: Optional[str] = None,
        start_point: Optional[str] = None,
        treeish: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Switches branches or checks out files. Wraps
        `git checkout <https://git-scm.com/docs/git-checkout>`_ (`git co`).

        Parameters
        ----------
        quiet : bool
        progress : bool
        no_progress : bool
        pathspec_from_file : :attr:`libvcs._internal.types.StrOrBytesPath`
        pathspec : :attr:`libvcs._internal.types.StrOrBytesPath` or list
            :attr:`libvcs._internal.types.StrOrBytesPath`
        force : bool
        ours : bool
        theirs : bool
        no_track : bool
        guess : bool
        no_guess : bool
        ignore_skip_worktree_bits : bool
        merge : bool
        _list : bool
        detach : bool
        patch : bool
        orphan : bool
        conflict : str
        overwrite_ignore : bool
        no_overwrite_ignore : bool
        commit : str
        branch : str
        new_branch : str
        start_point : str
        treeish : str

        Examples
        --------
        >>> git = Git(dir=git_local_clone.dir)

        >>> git.checkout()
        "Your branch is up to date with 'origin/master'."

        >>> git.checkout(branch='origin/master', pathspec='.')
        ''
        """
        local_flags: list[str] = []

        if quiet is True:
            local_flags.append("--quiet")
        if progress is True:
            local_flags.append("--progress")
        elif no_progress is True:
            local_flags.append("--no-progress")

        if force is True:
            local_flags.append("--force")

        if ours is True:
            local_flags.append("--ours")

        if theirs is True:
            local_flags.append("--theirs")

        if detach is True:
            local_flags.append("--detach")

        if orphan is not None:
            local_flags.append("--orphan")

        if conflict is not None:
            local_flags.append(f"--conflict={conflict}")

        if commit is not None:
            local_flags.append(commit)

        if branch is not None:
            local_flags.append(branch)

        if new_branch is not None:
            local_flags.append(new_branch)

        if start_point is not None:
            local_flags.append(start_point)

        if treeish is not None:
            local_flags.append(treeish)

        if recurse_submodules:
            local_flags.append("--recurse-submodules")
        elif no_recurse_submodules:
            local_flags.append("--no-recurse-submodules")

        if pathspec is not None:
            if not isinstance(pathspec, list):
                pathspec = [pathspec]
        else:
            pathspec = []

        return self.run(
            ["checkout", *local_flags, *(["--", *pathspec] if len(pathspec) else [])],
            check_returncode=False,
        )

    def status(
        self,
        *,
        verbose: Optional[bool] = None,
        long: Optional[bool] = None,
        short: Optional[bool] = None,
        branch: Optional[bool] = None,
        z: Optional[bool] = None,
        column: Optional[Union[bool, str]] = None,
        no_column: Optional[bool] = None,
        ahead_behind: Optional[bool] = None,
        no_ahead_behind: Optional[bool] = None,
        renames: Optional[bool] = None,
        no_renames: Optional[bool] = None,
        find_renames: Optional[Union[bool, str]] = None,
        porcelain: Optional[Union[bool, str]] = None,
        untracked_files: Optional[Literal["no", "normal", "all"]] = None,
        ignored: Optional[Literal["traditional", "no", "matching"]] = None,
        ignored_submodules: Optional[Literal["untracked", "dirty", "all"]] = None,
        pathspec: Optional[Union[StrOrBytesPath, list[StrOrBytesPath]]] = None,
        **kwargs: Any,
    ) -> str:
        """Status of working tree. Wraps
        `git status <https://git-scm.com/docs/git-status>`_.

        `git ls-files` has similar params (e.g. `z`)

        Parameters
        ----------
        verbose : bool
        long : bool
        short : bool
        branch : bool
        z : bool
        column : bool
        no_column : bool
        ahead_behind : bool
        no_ahead_behind : bool
        find_renames : bool
        no_find_renames : bool
        porcelain : str, bool
        untracked_files : "no", "normal", "all"
        ignored : "traditional", "no", "matching"
        ignored_submodules : "untracked", "dirty", "all"
        pathspec : :attr:`libvcs._internal.types.StrOrBytesPath` or list
            :attr:`libvcs._internal.types.StrOrBytesPath`

        Examples
        --------
        >>> git = Git(dir=git_local_clone.dir)

        >>> git.status()
        "On branch master..."

        >>> pathlib.Path(git_local_clone.dir / 'new_file.txt').touch()

        >>> git.status(porcelain=True)
        '?? new_file.txt'

        >>> git.status(porcelain='1')
        '?? new_file.txt'

        >>> git.status(porcelain='2')
        '? new_file.txt'

        >>> git.status(C=git_local_clone.dir / '.git', porcelain='2')
        '? new_file.txt'
        """
        local_flags: list[str] = []

        if verbose is True:
            local_flags.append("--verbose")

        if long is True:
            local_flags.append("--long")

        if short is True:
            local_flags.append("--short")

        if branch is True:
            local_flags.append("--branch")

        if z is True:
            local_flags.append("--z")

        if untracked_files is not None and isinstance(untracked_files, str):
            local_flags.append(f"--untracked-files={untracked_files}")

        if ignored is not None and isinstance(column, str):
            local_flags.append(f"--ignored={ignored}")

        if ignored_submodules is not None:
            if isinstance(column, str):
                local_flags.append(f"--ignored-submodules={ignored_submodules}")
            else:
                local_flags.append("--ignored-submodules")

        if column is not None:
            if isinstance(column, str):
                local_flags.append(f"--column={column}")
            else:
                local_flags.append("--column")
        elif no_column is not None:
            local_flags.append("--no-column")

        if porcelain is not None:
            if isinstance(porcelain, str):
                local_flags.append(f"--porcelain={porcelain}")
            else:
                local_flags.append("--porcelain")

        if find_renames is True:
            if isinstance(find_renames, str):
                local_flags.append(f"--find-renames={find_renames}")
            else:
                local_flags.append("--find-renames")

        if pathspec is not None:
            if not isinstance(pathspec, list):
                pathspec = [pathspec]
        else:
            pathspec = []

        return self.run(
            ["status", *local_flags, *(["--", *pathspec] if len(pathspec) else [])],
            check_returncode=False,
        )

    def config(
        self,
        *,
        replace_all: Optional[bool] = None,
        get: Optional[str] = None,
        get_all: Optional[bool] = None,
        get_regexp: Optional[str] = None,
        get_urlmatch: Optional[tuple[str, str]] = None,
        system: Optional[bool] = None,
        local: Optional[bool] = None,
        worktree: Optional[bool] = None,
        file: Optional[StrOrBytesPath] = None,
        blob: Optional[str] = None,
        remove_section: Optional[bool] = None,
        rename_section: Optional[bool] = None,
        unset: Optional[bool] = None,
        unset_all: Optional[bool] = None,
        _list: Optional[bool] = None,
        fixed_value: Optional[bool] = None,
        no_type: Optional[bool] = None,
        null: Optional[bool] = None,
        name_only: Optional[bool] = None,
        show_origin: Optional[bool] = None,
        show_scope: Optional[bool] = None,
        get_color: Optional[Union[str, bool]] = None,
        get_colorbool: Optional[Union[str, bool]] = None,
        default: Optional[bool] = None,
        _type: Optional[
            Literal["bool", "int", "bool-or-int", "path", "expiry-date", "color"]
        ] = None,
        edit: Optional[bool] = None,
        no_includes: Optional[bool] = None,
        includes: Optional[bool] = None,
        add: Optional[bool] = None,
        **kwargs: Any,
    ) -> str:
        """Status of working tree. Wraps
        `git status <https://git-scm.com/docs/git-status>`_.

        `git ls-files` has similar params (e.g. `z`)

        Parameters
        ----------
        replace_all : Optional[bool]
        get : Optional[bool]
        get_all : Optional[bool]
        get_regexp : Optional[bool]
        get_urlmatch : Optional[tuple[str, str]]
        system : Optional[bool]
        local : Optional[bool]
        worktree : Optional[bool]
        file : Optional[StrOrBytesPath]
        blob : Optional[str]
        remove_section : Optional[bool]
        rename_section : Optional[bool]
        unset : Optional[bool]
        unset_all : Optional[bool]
        _list : Optional[bool]
        fixed_value : Optional[bool]
        no_type : Optional[bool]
        null : Optional[bool]
        name_only : Optional[bool]
        show_origin : Optional[bool]
        show_scope : Optional[bool]
        get_color : Optional[Union[str, bool]]
        get_colorbool : Optional[Union[str, bool]]
        default : Optional[str]
        _type : "bool", "int", "bool-or-int", "path", "expiry-date", "color"
        edit : Optional[bool]
        no_includes : Optional[bool]
        includes : Optional[bool]
        add : Optional[bool]

        Examples
        --------
        >>> git = Git(dir=git_local_clone.dir)

        >>> git.config()
        'usage: git config ...'

        >>> git.config(_list=True)
        '...user.email=...'

        >>> git.config(get='color.diff')
        'auto'
        """
        local_flags: list[str] = []

        if replace_all is True:
            local_flags.append("--replace-all")

        if get is not None and isinstance(get, str):
            local_flags.extend(["--get", get])

        if get_regexp is not None and isinstance(get_regexp, str):
            local_flags.extend(["--get-regexp", get_regexp])

        if get_all is not None and isinstance(get_all, str):
            local_flags.extend(["--get-all", get_all])

        if get_urlmatch is not None and isinstance(get_urlmatch, tuple):
            local_flags.extend(["--get-urlmatch=", *get_urlmatch])

        if unset is not None and isinstance(unset, str):
            local_flags.extend(["--unset", unset])

        if unset_all is not None and isinstance(unset_all, str):
            local_flags.extend(["--unset-all", unset_all])

        if _list is True:
            local_flags.append("--list")

        if fixed_value is True:
            local_flags.append("--fixed-value")

        if no_type is True:
            local_flags.append("--no-type")

        if null is True:
            local_flags.append("--null")

        if name_only is True:
            local_flags.append("--name-only")

        if show_origin is True:
            local_flags.append("--show-origin")

        if show_scope is True:
            local_flags.append("--show-scope")

        if edit is True:
            local_flags.append("--edit")

        if system is True:
            local_flags.append("--system")

        if local is True:
            local_flags.append("--local")

        if worktree is True:
            local_flags.append("--worktree")

        if remove_section is True:
            local_flags.append("--remove-section")

        if rename_section is True:
            local_flags.append("--rename-section")

        if _type is not None and isinstance(_type, str):
            local_flags.extend(["--type", _type])

        if blob is not None and isinstance(blob, str):
            local_flags.extend(["--blob", blob])

        if file is not None:
            local_flags.extend(["--file", str(file)])

        if default is True:
            local_flags.append("--default")

        if includes is True:
            local_flags.append("--includes")

        if no_includes is True:
            local_flags.append("--no-includes")

        if add is True:
            local_flags.append("--add")

        if get_colorbool is not None:
            if isinstance(get_colorbool, str):
                local_flags.extend(["--get-colorbool", get_colorbool])
            else:
                local_flags.append("--get-colorbool")

        if get_color is not None:
            if isinstance(get_color, str):
                local_flags.extend(["--get-color", get_color])
            else:
                local_flags.append("--get-color")

        return self.run(
            ["config", *local_flags],
            check_returncode=False,
        )
