package main

import (
	"crypto/rand"
	_ "embed"
	"flag"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"strings"
)

// Word lists derived from public-domain sources. See SOURCES.md.
//
//go:embed words/adjectives.txt
var adjectivesData string

//go:embed words/nouns.txt
var nounsData string

//go:embed words/colors.txt
var colorsData string

//go:embed words/suffixes.txt
var suffixesData string

var (
	adjectives = nonEmpty(strings.Split(adjectivesData, "\n"))
	nouns      = nonEmpty(strings.Split(nounsData, "\n"))
	colors     = nonEmpty(strings.Split(colorsData, "\n"))
	suffixes   = nonEmpty(strings.Split(suffixesData, "\n"))
)

func nonEmpty(lines []string) []string {
	out := make([]string, 0, len(lines))
	for _, s := range lines {
		s = strings.TrimSpace(s)
		if s != "" {
			out = append(out, s)
		}
	}
	return out
}

func nrand(n int) int {
	v, err := rand.Int(rand.Reader, big.NewInt(int64(n)))
	if err != nil {
		panic(err)
	}
	return int(v.Int64())
}

func pick(list []string) string {
	return list[nrand(len(list))]
}

func pickUnique(list []string, exclude map[string]bool) string {
	for attempts := 0; attempts < 100; attempts++ {
		w := pick(list)
		if !exclude[w] {
			return w
		}
	}
	return pick(list) // fallback
}

func generate() string {
	used := make(map[string]bool)

	adj := pickUnique(adjectives, used)
	used[adj] = true

	col := pickUnique(colors, used)
	used[col] = true

	noun := pickUnique(nouns, used)
	used[noun] = true

	suf := pickUnique(suffixes, used)
	return adj + col + noun + suf
}

func main() {
	root := flag.String("r", "", "root directory for new workspace (default $HOME/Workspace)")
	flag.Parse()

	base := *root
	if base == "" {
		home, err := os.UserHomeDir()
		if err != nil {
			fmt.Fprintf(os.Stderr, "spawndir: cannot find home directory: %v\n", err)
			os.Exit(1)
		}
		base = filepath.Join(home, "Workspace")
	}

	name := generate()
	path := filepath.Join(base, name)

	if err := os.MkdirAll(path, 0755); err != nil {
		fmt.Fprintf(os.Stderr, "spawndir: cannot create directory: %v\n", err)
		os.Exit(1)
	}

	fmt.Println(path)
}
