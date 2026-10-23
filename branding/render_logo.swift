// Renders the Sakinah logo (open heart with سكينة inside) to PNG.
// CoreText shapes the Arabic properly; run from the repo root:
//   swift branding/render_logo.swift
import AppKit
import CoreText

let fontURL = URL(fileURLWithPath: "app/node_modules/@expo-google-fonts/amiri/700Bold/Amiri_700Bold.ttf")
CTFontManagerRegisterFontsForURL(fontURL as CFURL, .process, nil)

let navy = CGColor(srgbRed: 0x24 / 255, green: 0x30 / 255, blue: 0x44 / 255, alpha: 1)
let gold = CGColor(srgbRed: 0xC9 / 255, green: 0x8F / 255, blue: 0x4E / 255, alpha: 1)
let cream = CGColor(srgbRed: 0xF7 / 255, green: 0xF4 / 255, blue: 0xEF / 255, alpha: 1)
let white = CGColor(srgbRed: 1, green: 1, blue: 1, alpha: 1)

/// Unit heart (same curve as the brand sheet), y pointing down, spans x -1…1, y -1…0.78
func heart(cx: CGFloat, cy: CGFloat, s: CGFloat) -> CGPath {
    let p = CGMutablePath()
    func pt(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: cx + x * s, y: cy + y * s) }
    p.move(to: pt(0, 0.78))
    p.addCurve(to: pt(-1, -0.43), control1: pt(-0.55, 0.38), control2: pt(-1, -0.02))
    p.addCurve(to: pt(-0.46, -1), control1: pt(-1, -0.79), control2: pt(-0.73, -1))
    p.addCurve(to: pt(0, -0.69), control1: pt(-0.24, -1), control2: pt(-0.08, -0.87))
    p.addCurve(to: pt(0.46, -1), control1: pt(0.08, -0.87), control2: pt(0.24, -1))
    p.addCurve(to: pt(1, -0.43), control1: pt(0.73, -1), control2: pt(1, -0.79))
    p.addCurve(to: pt(0, 0.78), control1: pt(1, -0.02), control2: pt(0.55, 0.38))
    p.closeSubpath()
    return p
}

/// Draws the mark in a 1024-unit design space, scaled to `size` and centred on `center`.
func drawMark(_ ctx: CGContext, size: CGFloat, center: CGPoint, heartColor: CGColor, textColor: CGColor) {
    let k = size / 1024
    ctx.saveGState()
    // design space: origin top-left, y down, 1024 units
    ctx.translateBy(x: center.x - 512 * k, y: center.y - 512 * k)
    ctx.scaleBy(x: k, y: k)

    // Heart outline: outer heart minus inner heart, opened at the top notch
    ctx.beginTransparencyLayer(auxiliaryInfo: nil)
    ctx.setFillColor(heartColor)
    ctx.addPath(heart(cx: 512, cy: 545, s: 318)); ctx.fillPath()
    ctx.setBlendMode(.clear)
    ctx.addPath(heart(cx: 512, cy: 490, s: 250)); ctx.fillPath()
    ctx.fill(CGRect(x: 499, y: 180, width: 26, height: 200))
    ctx.setBlendMode(.normal)
    ctx.endTransparencyLayer()

    // سكينة, optically centred in the open heart
    let font = CTFontCreateWithName("Amiri-Bold" as CFString, 205, nil)
    let attrs: [NSAttributedString.Key: Any] = [.init(kCTFontAttributeName as String): font,
                                                .init(kCTForegroundColorAttributeName as String): textColor]
    let line = CTLineCreateWithAttributedString(NSAttributedString(string: "سكينة", attributes: attrs))
    let b = CTLineGetImageBounds(line, ctx)
    ctx.saveGState()
    ctx.translateBy(x: 512, y: 448)
    ctx.scaleBy(x: 1, y: -1) // CoreText draws y-up
    ctx.textPosition = CGPoint(x: -b.midX, y: -b.midY)
    CTLineDraw(line, ctx)
    ctx.restoreGState()
    ctx.restoreGState()
}

func png(_ path: String, px: Int, background: CGColor?, markSize: CGFloat,
         heartColor: CGColor = navy, textColor: CGColor = gold) {
    let ctx = CGContext(data: nil, width: px, height: px, bitsPerComponent: 8, bytesPerRow: 0,
                        space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    // flip to y-down
    ctx.translateBy(x: 0, y: CGFloat(px)); ctx.scaleBy(x: 1, y: -1)
    if let bg = background { ctx.setFillColor(bg); ctx.fill(CGRect(x: 0, y: 0, width: px, height: px)) }
    drawMark(ctx, size: markSize * CGFloat(px), center: CGPoint(x: CGFloat(px) / 2, y: CGFloat(px) / 2),
             heartColor: heartColor, textColor: textColor)
    let rep = NSBitmapImageRep(cgImage: ctx.makeImage()!)
    try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: path))
    print("wrote \(path) (\(px)px)")
}

let A = "app/assets/"
// The heart spans ~64% of the design square, so markSize 1.0 fills the icon nicely.
png(A + "icon.png", px: 1024, background: cream, markSize: 1.14)                 // iOS / store icon (opaque)
png(A + "splash-icon.png", px: 1024, background: nil, markSize: 1.0)            // splash, on cream
png(A + "android-icon-foreground.png", px: 512, background: nil, markSize: 0.78) // inside the 66% safe zone
png(A + "android-icon-background.png", px: 512, background: cream, markSize: 0)
png(A + "android-icon-monochrome.png", px: 432, background: nil, markSize: 0.78, heartColor: white, textColor: white)
png(A + "favicon.png", px: 48, background: cream, markSize: 1.3)
png(A + "logo.png", px: 512, background: nil, markSize: 1.0)                     // in-app logo
png("branding/sakinah-logo.png", px: 1024, background: cream, markSize: 1.14)
