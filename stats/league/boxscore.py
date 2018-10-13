from abc import ABC, abstractmethod
from stats.data.games import NbaGames, Game, Games
from stats.data.scoreboard import YesterdayScoreboard
from stats.data.teams import Team
from stats.support.tools.date import StampTime


class Info(ABC):
    """Abstract interface for some information object."""

    @abstractmethod
    def display(self) -> str:
        pass


class _TeamsInfo(Info):
    """Represent teams info about the win, loss and score dependency.
    Sample: ``ORL(2:3) vs SAS(3:2) 81 - 100``
    """

    def __init__(self, home_team: Team, visit_team: Team) -> None:
        self._home_team = home_team
        self._visit_team = visit_team

    def display(self) -> str:
        return f'{self._home_team.name()}({self._home_team.win()}:{self._home_team.loss()}) ' \
               f'vs {self._visit_team.name()}({self._visit_team.win()}:{self._visit_team.loss()}) ' \
               f'{self._home_team.score()} - {self._visit_team.score()}'


class _LineScoreInfo(Info):
    """Represent team linescores info per quarter.
    Sample: ``1st: 10 2nd: 10 3rd: 10 4th: 10 - 1st: 10 2nd: 10 3rd: 10 4th: 10``
    """

    def __init__(self, team: Team) -> None:
        self._team = team

    def display(self) -> str:
        return '1st:{} 2nd:{} 3rd:{} 4th:{}'.format(*self._team.line_score().all())


class GameScoresInfo(Info):
    """Represent game scores for a particular game.
    Sample:
    ```☆ ORL(2:3) vs SAS(3:2) 81 - 100
    Highlight - Preseason
    Linescores 1st:10 2nd:20 3rd:22 4th:29 - 1st:22 2nd:18 3rd:31 4th:2```
    """

    _star: str = '\u2606'

    def __init__(self, game: Game) -> None:
        self._teams = lambda home, visit: _TeamsInfo(home, visit)
        self._home_lines = lambda home: _LineScoreInfo(home)
        self._visit_lines = lambda visit: _LineScoreInfo(visit)
        self._game = game

    def display(self) -> str:
        hteam: Team = self._game.teams().home_team()
        vteam: Team = self._game.teams().visit_team()

        return f'{self._star} {self._teams(hteam, vteam).display()}\n Highlight - {self._game.highlight()}' \
               f'\n Linescores {self._home_lines(hteam).display()} - {self._visit_lines(vteam).display()}'


class GamesScoresInfo(Info):
    """Represent games scores for a multiple games."""

    def __init__(self, games: Games) -> None:
        self._games = games
        self._info = lambda game: GameScoresInfo(game)

    def display(self) -> str:
        return '\n\n'.join(map(lambda game: self._info(game).display(), self._games))


class YesterdayGameScores(Info):
    """Represent yestarday's scores for a set of games."""

    def __init__(self, date: StampTime) -> None:
        self._games = NbaGames(YesterdayScoreboard(date))
        self._games_info = GamesScoresInfo(self._games)

    def display(self) -> str:
        return f'{len(self._games)} games were played on {self._games.date()}\n {self._games_info.display()}'