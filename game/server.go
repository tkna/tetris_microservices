package main

import (
        "bytes"
        "net/http"
        "strconv"

        "github.com/labstack/echo"
)

type Game struct {
        Id      int     `json:"id"`
        Width   int     `json:"width"`
        Height  int     `json:"height"`
        Status  string  `json:"status"`
}

var games []Game

func main() {
        e := echo.New()
        e.POST("/games", newGame)
        e.Debug = true
        e.Logger.Debug(e.Start(":80"))
}

func newGame(c echo.Context) error {
        g := new(Game)
        if err := c.Bind(g); err != nil {
                return err
        }

        g.Id = len(games)
        g.Status = "started"
        games = append(games, *g)

        err := createField(g.Width, g.Height)
        if err != nil {
                return err
        }

        return c.JSON(http.StatusOK, g)
}

func createField(width int, height int) error {
        json := `{"width":` + strconv.Itoa(width) + `,"height":` + strconv.Itoa(height) + `}`
        URL := "http://field/field"
        res, err := http.Post(URL, "application/json", bytes.NewBuffer([]byte(json)))
        if err != nil {
                return err
        }
        defer res.Body.Close()
        return err
}
