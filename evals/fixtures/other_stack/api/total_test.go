package fixture

import "testing"

func TestTotal(t *testing.T) {
	if Total(10, 2, 3) != 17 { t.Fatal("discount missing") }
}
