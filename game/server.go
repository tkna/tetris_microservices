package main

import (
        "bytes"
        "io/ioutil"
        "encoding/json"
//        "fmt"
        "net/http"
        "strconv"
        "time"

        "github.com/labstack/echo"
)

type Game struct {
        Id      int     `json:"id"`
        Width   int     `json:"width"`
        Height  int     `json:"height"`
        Status  string  `json:"status"`
}

type MinoInstance struct {
        Id int                  `json:"id"`
        MinoId int              `json:"mino_id`
        X int                   `json:"x"`
        Y int                   `json:"y"`
        Coords []Coordinate     `json:"coords"`
        ColorId int             `json:"color_id`
}

type Coordinate struct {
        X int   `json:"x"`
        Y int   `json:"y"`
}

type CreateMinoInstanceResponse struct {
        Result string   `json:"result"`
        Message string  `json:"message`
        Instance MinoInstance   `json:"instance"`
}

type MoveInstanceResponse struct {
        Result string   `json:"result"`
        Message string  `json:"message"`
}

type MoveInstanceRequest struct {
        Operation string `json:"operation"`
}

var games []Game

func main() {
        e := echo.New()
        e.POST("/games", newGame)
        e.POST("/move", move)
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

        go mainLoop()

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

func createMinoInstance() (*MinoInstance, error) {
        URL := "http://mino/instances"
        jsn := ""
        res, err := http.Post(URL, "application/json", bytes.NewBuffer([]byte(jsn)))
        if err != nil {
                return nil, err
        }
        defer res.Body.Close()

        body, _ := ioutil.ReadAll(res.Body)
        var resp CreateMinoInstanceResponse
        json.Unmarshal(body, &resp)

        if resp.Result == "success" {
                return &resp.Instance, err
        }
        if resp.Result == "failed" {
                if resp.Message == "collision" {
                        return nil, err
                }
        }

        return nil, err
}

func moveInstance(op string) (*MoveInstanceResponse, error) {
        client := &http.Client{}

        URL := "http://mino/instances/0"
        jsn := `{"operation":"` + op + `"}`
        
        req, err := http.NewRequest(http.MethodPut, URL, bytes.NewBuffer([]byte(jsn)))
        if err != nil {
                return nil, err
        }

        req.Header.Set("Content-Type", "application/json; charset=utf-8")
        resp, err := client.Do(req)
        if err != nil {
                return nil, err
        }

        defer resp.Body.Close()

        body, _ := ioutil.ReadAll(resp.Body)
        var res MoveInstanceResponse
        json.Unmarshal(body, &res)

        return &res, err
}

func move(c echo.Context) error {
        req := new(MoveInstanceRequest)
        if err := c.Bind(req); err != nil {
                return err
        }

        if games[0].Status != "started" {
                response := MoveInstanceResponse{Result: "failed", Message: "Status is not started"}
                return c.JSON(http.StatusOK, response)
        }

        res, err := moveInstance(req.Operation)
        if err != nil {
                return err
        }
        return c.JSON(http.StatusOK, res)
}

func mainLoop() {
        for games[0].Status != "GameOver" {
                instance, err := createMinoInstance()
                if err != nil {
                        panic(err)
                }
                if instance != nil {
                        falling := true
                        for falling == true {
                                time.Sleep(time.Second * 1)
                                res, err := moveInstance("down")
                                if err != nil {
                                        panic(err)
                                }
                                if res.Result == "success" {
                                        continue
                                } else {
                                        break
                                }
                        }
                } else {
                        games[0].Status = "GameOver"
                }
        }
}