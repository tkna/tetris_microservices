package main

import (
        "bytes"
        "io/ioutil"
        "encoding/json"
//        "fmt"
        "log"
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
        instance *MinoInstance
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
        Result string                   `json:"result"`
        Message string                  `json:"message"`
        Data []map[string]string        `json:"data"`
}

type MoveInstanceRequest struct {
        GameId int              `json:"gameId"`
        Operation string        `json:"operation"`
}

var games []Game

func main() {
        e := echo.New()
        e.POST("/games", newGame)
        e.GET("/games/:id", getGameById)
        e.POST("/move", move)
        e.Debug = true
        e.Logger.Debug(e.Start(":80"))
}

func newGame(c echo.Context) error {
        log.Println("newGame")
        g := new(Game)
        if err := c.Bind(g); err != nil {
                return err
        }

        // Use the gameId whose status == "GameOver" for the new game.
        // Basically it uses gameId=0 and gameId=1 alternately because mainLoop's termination is asynchronous.
        gameId := -1          
        for i, game := range games {
                instanceId := games[len(games)-1].instance.Id
                _, err := deleteInstance(instanceId)
                if err != nil {
                        return err
                }
                if game.Status == "GameOver" {
                        if gameId == -1 {
                                gameId = i
                        }
                } else if game.Status == "started" {
                        games[i].Status = "GameOver"
                }
        }

        g.Status = "started"
        if gameId == -1 {
                g.Id = len(games)
                games = append(games, *g)
        } else {
                g.Id = gameId
                games[gameId] = *g
        }
        
        err := createField(g.Width, g.Height)
        if err != nil {
                return err
        }

        go mainLoop(g.Id)

        return c.JSON(http.StatusOK, g)
}

func getGameById(c echo.Context) error {
        gameId, _ := strconv.Atoi(c.Param("id"))
        return c.JSON(http.StatusOK, games[gameId])
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

func getInstance(instanceId int) (*MinoInstance, error) {
        URL := "http://mino/instances/" + strconv.Itoa(instanceId)
        res, err := http.Get(URL)
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
                return nil, err
        }

        return nil, err
}

func moveInstance(instanceId int, op string) (*MoveInstanceResponse, error) {
        log.Printf("moveInstance: instanceId=%d, op=%s\n", instanceId, op)
        client := &http.Client{}

        URL := "http://mino/instances/" + strconv.Itoa(instanceId)
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
        log.Println(res)

        return &res, err
}

func deleteInstance(instanceId int) (*MoveInstanceResponse, error) {
        client := &http.Client{}

        URL := "http://mino/instances/" + strconv.Itoa(instanceId)
        jsn := ""
        
        req, err := http.NewRequest(http.MethodDelete, URL, bytes.NewBuffer([]byte(jsn)))
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

        if games[req.GameId].Status != "started" {
                response := MoveInstanceResponse{Result: "failed", Message: "Status is not started"}
                return c.JSON(http.StatusOK, response)
        }

        res, err := moveInstance(games[req.GameId].instance.Id, req.Operation)
        if err != nil {
                return err
        }
        if res.Message == "landed" { 
                log.Println("landed")
                log.Println(res)
                removed_lines, _ := strconv.Atoi(res.Data[0]["value"])
                log.Println("removed_lines:", removed_lines)
                if removed_lines > 0 {
                        log.Println("removed: ", removed_lines)
                }
        }
        return c.JSON(http.StatusOK, res)
}

func mainLoop(gameId int) {
        log.Printf("mainLoop: gameId=%d\n", gameId)
        ticker := time.NewTicker(1 * time.Second)
        defer ticker.Stop()

        for {
                select {
                case <-ticker.C:
                        log.Println("ticker")
                        log.Printf("gameId: %d\n", gameId)
                        if games[gameId].Status == "GameOver" {
                                log.Printf("gameId:%d GameOver\n", gameId)
                                return
                        }

                        var ins *MinoInstance
                        var err error
                        if games[gameId].instance != nil {
                                instanceId := games[gameId].instance.Id
                                ins, err = getInstance(instanceId)
                                if err != nil {
                                        panic(err)
                                }
                        }

                        if ins == nil {
                                log.Println("Create MinoInstance")
                                instance, err := createMinoInstance()
                                if err != nil {
                                        panic(err)
                                }
                                if instance == nil {
                                        games[gameId].Status = "GameOver"
                                } else {
                                        games[gameId].instance = instance
                                }
                        } else {
                                log.Println("MinoInstance down")
                                _, err := moveInstance(games[gameId].instance.Id, "down")
                                if err != nil {
                                        panic(err)
                                }
                        }
                        
                }
        }
}