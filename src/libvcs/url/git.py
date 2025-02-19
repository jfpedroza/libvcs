"""This module is an all-in-one parser and validator for Git URLs.

- Detection: :meth:`GitURL.is_valid()`
- Parse:

  compare to :class:`urllib.parse.ParseResult`

  - Compatibility focused: :class:`GitURL`: Will work with ``git(1)`` as well as
    ``pip(1)`` style URLs

    - Output ``git(1)`` URL: :meth:`GitURL.to_url()`
  - Strict ``git(1)`` compatibility: :class:`GitBaseURL`.

    - Output ``git(1)`` URL: :meth:`GitBaseURL.to_url()`
- Extendable via :class:`~libvcs.url.base.RuleMap`,
  :class:`~libvcs.url.base.Rule`
"""

import dataclasses
import re
from typing import Optional

from libvcs._internal.dataclasses import SkipDefaultFieldsReprMixin

from .base import Rule, RuleMap, URLProtocol

# Credit, pip (license: MIT):
# https://github.com/pypa/pip/blob/22.1.2/src/pip/_internal/vcs/git.py#L39-L52
# We modified it to have groupings
SCP_REGEX = r"""
    # Optional user, e.g. 'git@'
    ((?P<user>\w+)@)?
    # Server, e.g. 'github.com'.
    (?P<hostname>([^/:]+))
    (?P<separator>:)
    # The server-side path. e.g. 'user/project.git'. Must start with an
    # alphanumeric character so as not to be confusable with a Windows paths
    # like 'C:/foo/bar' or 'C:\foo\bar'.
    (?P<path>(\w[^:.]+))
    """

RE_PATH = r"""
    ((?P<user>\w+)@)?
    (?P<hostname>([^/:]+))
    (:(?P<port>\d{1,5}))?
    (?P<separator>[:,/])?
    (?P<path>
      (\w[^:.@]*)  # cut the path at . to negate .git, @ from pip
    )?
"""

RE_SCHEME = r"""
    (?P<scheme>
      (
        http|https
      )
    )
"""

RE_SUFFIX = r"(?P<suffix>\.git)"
# Some https repos have .git at the end, e.g. https://github.com/org/repo.git


DEFAULT_RULES: list[Rule] = [
    Rule(
        label="core-git-https",
        description="Vanilla git pattern, URL ending with optional .git suffix",
        pattern=re.compile(
            rf"""
        ^{RE_SCHEME}
        ://
        {RE_PATH}
        {RE_SUFFIX}?
        """,
            re.VERBOSE,
        ),
    ),
    # ends with .git. Including ones starting with https://
    # e.g. https://github.com/vcs-python/libvcs.git
    Rule(
        label="core-git-scp",
        description="Vanilla scp(1) / ssh(1) type URL",
        pattern=re.compile(
            rf"""
        ^(?P<scheme>ssh)?
        {SCP_REGEX}
        {RE_SUFFIX}?
        """,
            re.VERBOSE,
        ),
        defaults={"username": "git"},
    ),
    # SCP-style URLs, e.g. git@
]
"""Core regular expressions. These are patterns understood by ``git(1)``

See also: https://git-scm.com/docs/git-clone#URLS
"""


#
# Third-party URLs, e.g. npm, pip, etc.
#
RE_PIP_SCHEME = r"""
    (?P<scheme>
      (
        git\+ssh|
        git\+https|
        git\+http|
        git\+file
      )
    )
"""

RE_PIP_SCP_SCHEME = r"""
    (?P<scheme>
      (
        git\+ssh|
        git\+file
      )
    )
"""

RE_PIP_REV = r"""
    (@(?P<rev>.*))
"""


PIP_DEFAULT_RULES: list[Rule] = [
    Rule(
        label="pip-url",
        description="pip-style git URL",
        pattern=re.compile(
            rf"""
        {RE_PIP_SCHEME}
        ://
        {RE_PATH}
        {RE_SUFFIX}?
        {RE_PIP_REV}?
        """,
            re.VERBOSE,
        ),
        is_explicit=True,
    ),
    Rule(
        label="pip-scp-url",
        description="pip-style git ssh/scp URL",
        pattern=re.compile(
            rf"""
        {RE_PIP_SCP_SCHEME}
        {SCP_REGEX}?
        {RE_SUFFIX}?
        {RE_PIP_REV}?
        """,
            re.VERBOSE,
        ),
        is_explicit=True,
    ),
    # file://, RTC 8089, File:// https://datatracker.ietf.org/doc/html/rfc8089
    Rule(
        label="pip-file-url",
        description="pip-style git+file:// URL",
        pattern=re.compile(
            rf"""
        (?P<scheme>git\+file)://
        (?P<path>[^@]*)
        {RE_PIP_REV}?
        """,
            re.VERBOSE,
        ),
        is_explicit=True,
    ),
]
"""pip-style git URLs.

Examples of PIP-style git URLs (via pip.pypa.io)::

    MyProject @ git+ssh://git.example.com/MyProject
    MyProject @ git+file:///home/user/projects/MyProject
    MyProject @ git+https://git.example.com/MyProject

Refs (via pip.pypa.io)::

    MyProject @ git+https://git.example.com/MyProject.git@master
    MyProject @ git+https://git.example.com/MyProject.git@v1.0
    MyProject @ git+https://git.example.com/MyProject.git@da39a3ee5e6b4b0d3255bfef95601890afd80709
    MyProject @ git+https://git.example.com/MyProject.git@refs/pull/123/head

Notes
-----

- https://pip.pypa.io/en/stable/topics/vcs-support/
"""  # NOQA: E501

NPM_DEFAULT_RULES: list[Rule] = []
"""NPM-style git URLs.

Git URL pattern (from docs.npmjs.com)::

   <protocol>://[<user>[:<password>]@]<hostname>[:<port>][:][/]<path>[#<commit-ish> | #semver:<semver>]

Examples of NPM-style git URLs (from docs.npmjs.com)::

    ssh://git@github.com:npm/cli.git#v1.0.27
    git+ssh://git@github.com:npm/cli#semver:^5.0
    git+https://isaacs@github.com/npm/cli.git
    git://github.com/npm/cli.git#v1.0.27

Notes
-----

- https://docs.npmjs.com/cli/v8/configuring-npm/package-json#git-urls-as-dependencies
"""  # NOQA: E501


@dataclasses.dataclass(repr=False)
class GitBaseURL(URLProtocol, SkipDefaultFieldsReprMixin):
    """Git repository location. Parses URLs on initialization.

    Examples
    --------
    >>> GitBaseURL(url='https://github.com/vcs-python/libvcs.git')
    GitBaseURL(url=https://github.com/vcs-python/libvcs.git,
            scheme=https,
            hostname=github.com,
            path=vcs-python/libvcs,
            suffix=.git,
            rule=core-git-https)

    >>> myrepo = GitBaseURL(url='https://github.com/myproject/myrepo.git')

    >>> myrepo.hostname
    'github.com'

    >>> myrepo.path
    'myproject/myrepo'

    >>> GitBaseURL(url='git@github.com:vcs-python/libvcs.git')
    GitBaseURL(url=git@github.com:vcs-python/libvcs.git,
            user=git,
            hostname=github.com,
            path=vcs-python/libvcs,
            suffix=.git,
            rule=core-git-scp)

    - Compatibility checking: :meth:`GitBaseURL.is_valid()`
    - URLs compatible with ``git(1)``: :meth:`GitBaseURL.to_url()`

    Attributes
    ----------
    rule : str
        name of the :class:`~libvcs.url.base.Rule`
    """

    url: str
    scheme: Optional[str] = None
    user: Optional[str] = None
    hostname: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None

    # Decoration
    suffix: Optional[str] = None

    rule: Optional[str] = None
    rule_map: RuleMap = RuleMap(_rule_map={m.label: m for m in DEFAULT_RULES})

    def __post_init__(self) -> None:
        url = self.url
        for rule in self.rule_map.values():
            match = re.match(rule.pattern, url)
            if match is None:
                continue
            groups = match.groupdict()
            setattr(self, "rule", rule.label)
            for k, v in groups.items():
                setattr(self, k, v)

            for k, v in rule.defaults.items():
                if getattr(self, k, None) is None:
                    setattr(self, k, rule.defaults[k])

    @classmethod
    def is_valid(cls, url: str, is_explicit: Optional[bool] = None) -> bool:
        """Whether URL is compatible with VCS or not.

        Examples
        --------

        >>> GitBaseURL.is_valid(url='https://github.com/vcs-python/libvcs.git')
        True

        >>> GitBaseURL.is_valid(url='git@github.com:vcs-python/libvcs.git')
        True

        >>> GitBaseURL.is_valid(url='notaurl')
        False

        **Unambiguous VCS detection**

        Sometimes you may want to match a VCS exclusively, without any change for, e.g.
        in order to outright detect the VCS system being used.

        >>> GitBaseURL.is_valid(
        ...     url='git@github.com:vcs-python/libvcs.git', is_explicit=True
        ... )
        False

        In this case, check :meth:`GitPipURL.is_valid` or :meth:`GitURL.is_valid`'s
        examples.
        """
        if is_explicit is not None:
            return any(
                re.search(rule.pattern, url)
                for rule in cls.rule_map.values()
                if rule.is_explicit == is_explicit
            )
        return any(re.search(rule.pattern, url) for rule in cls.rule_map.values())

    def to_url(self) -> str:
        """Return a ``git(1)``-compatible URL. Can be used with ``git clone``.

        Examples
        --------

        >>> git_url = GitBaseURL(url='git@github.com:vcs-python/libvcs.git')

        >>> git_url
        GitBaseURL(url=git@github.com:vcs-python/libvcs.git,
                user=git,
                hostname=github.com,
                path=vcs-python/libvcs,
                suffix=.git,
                rule=core-git-scp)

        Switch repo libvcs -> vcspull:

        >>> git_url.path = 'vcs-python/vcspull'

        >>> git_url.to_url()
        'git@github.com:vcs-python/vcspull.git'

        Switch them to gitlab:

        >>> git_url.hostname = 'gitlab.com'

        >>> git_url.to_url()
        'git@gitlab.com:vcs-python/vcspull.git'

        todo
        ----

        - Formats: Show an example converting a github url from ssh -> https format,
          and the other way around.
        """
        if self.scheme is not None:
            parts = [self.scheme, "://", self.hostname, "/", self.path]
        else:
            parts = [self.user or "git", "@", self.hostname, ":", self.path]

        if self.suffix:
            parts.append(self.suffix)

        return "".join(part for part in parts if isinstance(part, str))


@dataclasses.dataclass(repr=False)
class GitPipURL(GitBaseURL, URLProtocol, SkipDefaultFieldsReprMixin):
    """Supports pip git URLs."""

    # commit-ish (rev): tag, branch, ref
    rev: Optional[str] = None

    rule_map: RuleMap = RuleMap(_rule_map={m.label: m for m in PIP_DEFAULT_RULES})

    def to_url(self) -> str:
        """Exports a pip-compliant URL.

        Examples
        --------

        >>> git_url = GitPipURL(
        ...     url='git+ssh://git@bitbucket.example.com:7999/PROJ/repo.git'
        ... )

        >>> git_url
        GitPipURL(url=git+ssh://git@bitbucket.example.com:7999/PROJ/repo.git,
                scheme=git+ssh,
                user=git,
                hostname=bitbucket.example.com,
                port=7999,
                path=PROJ/repo,
                suffix=.git,
                rule=pip-url)

        >>> git_url.path = 'libvcs/vcspull'

        >>> git_url.to_url()
        'git+ssh://bitbucket.example.com/libvcs/vcspull.git'

        It also accepts revisions, e.g. branch, tag, ref:

        >>> git_url = GitPipURL(
        ...     url='git+https://github.com/vcs-python/libvcs.git@v0.10.0'
        ... )

        >>> git_url
        GitPipURL(url=git+https://github.com/vcs-python/libvcs.git@v0.10.0,
                scheme=git+https,
                hostname=github.com,
                path=vcs-python/libvcs,
                suffix=.git,
                rule=pip-url,
                rev=v0.10.0)

        >>> git_url.path = 'libvcs/vcspull'

        >>> git_url.to_url()
        'git+https://github.com/libvcs/vcspull.git@v0.10.0'
        """
        url = super().to_url()

        if self.rev:
            url = f"{url}@{self.rev}"

        return url

    @classmethod
    def is_valid(cls, url: str, is_explicit: Optional[bool] = None) -> bool:
        """Whether URL is compatible with Pip Git's VCS URL pattern or not.

        Examples
        --------

        Will **not** match normal ``git(1)`` URLs, use :meth:`GitURL.is_valid` for that.

        >>> GitPipURL.is_valid(url='https://github.com/vcs-python/libvcs.git')
        False

        >>> GitPipURL.is_valid(url='git@github.com:vcs-python/libvcs.git')
        False

        Pip-style URLs:

        >>> GitPipURL.is_valid(url='git+https://github.com/vcs-python/libvcs.git')
        True

        >>> GitPipURL.is_valid(url='git+ssh://git@github.com:vcs-python/libvcs.git')
        True

        >>> GitPipURL.is_valid(url='notaurl')
        False

        **Explicit VCS detection**

        Pip-style URLs are prefixed with the VCS name in front, so its rule_map can
        unambigously narrow the type of VCS:

        >>> GitPipURL.is_valid(
        ...     url='git+ssh://git@github.com:vcs-python/libvcs.git', is_explicit=True
        ... )
        True
        """
        return super().is_valid(url=url, is_explicit=is_explicit)


@dataclasses.dataclass(repr=False)
class GitURL(GitPipURL, GitBaseURL, URLProtocol, SkipDefaultFieldsReprMixin):
    """Batteries included URL Parser. Supports git(1) and pip URLs.

    **Ancestors (MRO)**
    This URL parser inherits methods and attributes from the following parsers:

    - :class:`GitPipURL`

      - :meth:`GitPipURL.to_url`
    - :class:`GitBaseURL`

      - :meth:`GitBaseURL.to_url`
    """

    rule_map: RuleMap = RuleMap(
        _rule_map={m.label: m for m in [*DEFAULT_RULES, *PIP_DEFAULT_RULES]}
    )

    @classmethod
    def is_valid(cls, url: str, is_explicit: Optional[bool] = None) -> bool:
        r"""Whether URL is compatible included Git URL rule_map or not.

        Examples
        --------

        **Will** match normal ``git(1)`` URLs, use :meth:`GitURL.is_valid` for that.

        >>> GitURL.is_valid(url='https://github.com/vcs-python/libvcs.git')
        True

        >>> GitURL.is_valid(url='git@github.com:vcs-python/libvcs.git')
        True

        Pip-style URLs:

        >>> GitURL.is_valid(url='git+https://github.com/vcs-python/libvcs.git')
        True

        >>> GitURL.is_valid(url='git+ssh://git@github.com:vcs-python/libvcs.git')
        True

        >>> GitURL.is_valid(url='notaurl')
        False

        **Explicit VCS detection**

        Pip-style URLs are prefixed with the VCS name in front, so its rule_map can
        unambigously narrow the type of VCS:

        >>> GitURL.is_valid(
        ...     url='git+ssh://git@github.com:vcs-python/libvcs.git', is_explicit=True
        ... )
        True

        Below, while it's GitHub, that doesn't necessarily mean that the URL itself
        is conclusively a `git` URL (e.g. the pattern is too lax):

        >>> GitURL.is_valid(
        ...     url='git@github.com:vcs-python/libvcs.git', is_explicit=True
        ... )
        False

        You could create a GitHub rule that consider github.com hostnames to be
        exclusively git:

        >>> GitHubRule = Rule(
        ...     # Since github.com exclusively serves git repos, make explicit
        ...     label='gh-rule',
        ...     description='Matches github.com https URLs, exact VCS match',
        ...     pattern=re.compile(
        ...         rf'''
        ...         ^(?P<scheme>ssh)?
        ...         ((?P<user>\w+)@)?
        ...         (?P<hostname>(github.com)+):
        ...         (?P<path>(\w[^:]+))
        ...         {RE_SUFFIX}?
        ...         ''',
        ...         re.VERBOSE,
        ...     ),
        ...     is_explicit=True,
        ...     defaults={
        ...         'hostname': 'github.com'
        ...     }
        ... )

        >>> GitURL.rule_map.register(GitHubRule)

        >>> GitURL.is_valid(
        ...     url='git@github.com:vcs-python/libvcs.git', is_explicit=True
        ... )
        True

        >>> GitURL(url='git@github.com:vcs-python/libvcs.git').rule
        'gh-rule'

        This is just us cleaning up:

        >>> GitURL.rule_map.unregister('gh-rule')

        >>> GitURL(url='git@github.com:vcs-python/libvcs.git').rule
        'core-git-scp'
        """
        return super().is_valid(url=url, is_explicit=is_explicit)

    def to_url(self) -> str:
        """Return a ``git(1)``-compatible URL. Can be used with ``git clone``.

        Examples
        --------

        SSH style URL:

        >>> git_url = GitURL(url='git@github.com:vcs-python/libvcs')

        >>> git_url.path = 'vcs-python/vcspull'

        >>> git_url.to_url()
        'git@github.com:vcs-python/vcspull'

        HTTPs URL:

        >>> git_url = GitURL(url='https://github.com/vcs-python/libvcs.git')

        >>> git_url.path = 'vcs-python/vcspull'

        >>> git_url.to_url()
        'https://github.com/vcs-python/vcspull.git'

        Switch them to gitlab:

        >>> git_url.hostname = 'gitlab.com'

        >>> git_url.to_url()
        'https://gitlab.com/vcs-python/vcspull.git'

        Pip style URL, thanks to this class implementing :class:`GitPipURL`:

        >>> git_url = GitURL(url='git+ssh://git@github.com/vcs-python/libvcs')

        >>> git_url.hostname = 'gitlab.com'

        >>> git_url.to_url()
        'git+ssh://gitlab.com/vcs-python/libvcs'

        See also
        --------

        :meth:`GitBaseURL.to_url`, :meth:`GitPipURL.to_url`
        """
        return super().to_url()
