// Build-only helper. The installed clock application never needs Go.
package main

import (
    "encoding/binary"
    "fmt"
    "hash/crc32"
    "io"
    "os"
    "time"
    dmg "github.com/jetbrains/go-dmg-writer"
)

func main() {
    if len(os.Args) != 3 { fmt.Fprintln(os.Stderr, "usage: dmg-writer SOURCE OUTPUT"); os.Exit(2) }
    image := &dmg.DMG{
        VolumeName: "Smart Clock Setup",
        OwnerID: dmg.OwnerIDUnset,
        GroupID: dmg.OwnerIDUnset,
        Time: time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC),
        PartitionMap: true,
    }
    if err := image.Create(os.Args[1], os.Args[2], dmg.ModeReadOnlyCompressed); err != nil {
        fmt.Fprintln(os.Stderr, err); os.Exit(1)
    }
    // This pinned writer computes its data-fork CRC before compression. UDIF
    // readers expect the checksum of the encoded data fork; leave the separate
    // uncompressed block-table and master checksums unchanged.
    file, err := os.OpenFile(os.Args[2], os.O_RDWR, 0)
    if err != nil { panic(err) }
    defer file.Close()
    stat, err := file.Stat()
    if err != nil { panic(err) }
    footer := make([]byte, 512)
    if _, err = file.ReadAt(footer, stat.Size()-512); err != nil { panic(err) }
    if string(footer[:4]) != "koly" { panic("invalid UDIF trailer") }
    offset := int64(binary.BigEndian.Uint64(footer[24:32]))
    length := int64(binary.BigEndian.Uint64(footer[32:40]))
    if offset < 0 || length < 0 || offset+length > stat.Size()-512 { panic("invalid UDIF data fork") }
    checksum := crc32.NewIEEE()
    if _, err = io.Copy(checksum, io.NewSectionReader(file, offset, length)); err != nil { panic(err) }
    binary.BigEndian.PutUint32(footer[88:92], checksum.Sum32())
    if _, err = file.WriteAt(footer, stat.Size()-512); err != nil { panic(err) }
    if err = file.Sync(); err != nil { panic(err) }
}
