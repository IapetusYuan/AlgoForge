---
id: 3658
title: GCD of Odd and Even Sums
slug: gcd-of-odd-and-even-sums
difficulty: Easy
tags: [Math, Number Theory]
url: https://leetcode.com/problems/gcd-of-odd-and-even-sums/
patterns: [math, number-theory]
time_complexity: O(1)
space_complexity: O(1)
date_solved: 2026-07-21
revisit: 2026-08-04
status: solved
---

# 3658. GCD of Odd and Even Sums

> Easy · Math, Number Theory · [原題連結](https://leetcode.com/problems/gcd-of-odd-and-even-sums/)

## 題目原文
You are given an integer `n`. Your task is to compute the **GCD** (greatest common divisor) of two values:

	- 
	`sumOdd`: the sum of the smallest `n` positive odd numbers.

	

	- 
	`sumEven`: the sum of the smallest `n` positive even numbers.

	

Return the GCD of `sumOdd` and `sumEven`.

 

Example 1:**

**Input:** n = 4

**Output:** 4

**Explanation:**

	- Sum of the first 4 odd numbers `sumOdd = 1 + 3 + 5 + 7 = 16`

	- Sum of the first 4 even numbers `sumEven = 2 + 4 + 6 + 8 = 20`

Hence, `GCD(sumOdd, sumEven) = GCD(16, 20) = 4`.

Example 2:**

**Input:** n = 5

**Output:** 5

**Explanation:**

	- Sum of the first 5 odd numbers `sumOdd = 1 + 3 + 5 + 7 + 9 = 25`

	- Sum of the first 5 even numbers `sumEven = 2 + 4 + 6 + 8 + 10 = 30`

Hence, `GCD(sumOdd, sumEven) = GCD(25, 30) = 5`.

 

**Constraints:**

	- `1 <= n <= 10​​​​​​​00`

---
<!-- 以下 8 段由 @algoforge-coach 填寫 -->

## 1. 題目摘要
給定正整數 `n`（`1 <= n <= 1000`），設 `sumOdd` 為前 `n` 個正奇數之和、`sumEven` 為前 `n` 個正偶數之和，求 `gcd(sumOdd, sumEven)`。輸入輸出都是單一整數，範圍極小（`n ≤ 1000`），這種「小範圍 + 求某個數論結果」的題型，通常暗示答案背後有封閉式公式，而不是要你真的跑迴圈或呼叫 `gcd` 函式去硬算。

## 2. 怎麼切入這題（思維框架）
**第一個天真念頭**：既然要求 GCD，直覺會想「先把兩個 sum 算出來，再套 Euclidean algorithm（輾轉相除法）求 GCD」。畢竟題目字面上就是「算兩個和，再求最大公因數」，照樣造句寫程式碼幾乎零思考就能過。

**但看到的訊號應該讓你多想一步**：
- 「前 n 個奇數之和」「前 n 個偶數之和」是非常經典的等差數列求和公式，看到這種措辞要立刻反射性地想到公式化簡，而不是寫迴圈累加。
- 資料範圍 `n ≤ 1000` 小到誇張，如果正解需要 O(n) 或以上的迴圈，通常不會出這麼小的上限；小範圍常常是「out of subtlety」的訊號 —— 暗示這題的真正難點不在效能，而在**能不能把公式化簡到底**。
- 標籤是 `Math / Number Theory`，不是 `Simulation`，代表評測方希望你做代數推導，而不是模擬過程。

**正確切入點**：先把 `sumOdd`、`sumEven` 用封閉式公式表示：
- `sumOdd = 1 + 3 + 5 + ... + (2n-1) = n²`（等差數列求和，或用「奇數和 = 完全平方數」的經典結論）
- `sumEven = 2 + 4 + 6 + ... + 2n = n(n+1)`（等差數列求和，或直接是 `2 × (1+2+...+n) = 2 × n(n+1)/2`）

接著求 `gcd(n², n(n+1))`。利用「提出公因子」的技巧：`gcd(n², n(n+1)) = n × gcd(n, n+1)`。而 `n` 與 `n+1` 是相鄰整數，相鄰整數必互質（`gcd(n, n+1) = 1`，可用反證法：若 `d` 同時整除 `n` 與 `n+1`，則 `d` 也整除 `(n+1) - n = 1`，故 `d = 1`）。

所以最終答案就是 `gcd(n², n(n+1)) = n × 1 = n`。**整題的答案就是輸入本身**，不需要算任何 sum、也不需要呼叫任何 GCD 函式。

## 3. 核心觀念
這題考的是「用代數手法把問題化簡到底」的數論直覺，而不是任何資料結構或演算法技巧。核心觀念有兩個：
1. **等差數列封閉式求和**：把「累加 n 項」的過程用公式一步到位，避免不必要的迴圈。
2. **相鄰整數互質（`gcd(n, n+1) = 1`）**：這是數論裡最基本也最常被拿來簡化 GCD 表達式的性質，一旦看到 GCD 的兩個引數可以被拆成「公因子 × 兩個相鄰數」，就該直接聯想到答案會塌縮成那個公因子。

## 4. 解法
### Java（主）
```java
class Solution {
    public int gcdOfOddEvenSums(int n) {
        // sumOdd = n^2, sumEven = n*(n+1)
        // gcd(n^2, n*(n+1)) = n * gcd(n, n+1) = n * 1 = n
        // 因為 n 與 n+1 相鄰必互質，數學推導後答案恆為 n
        return n;
    }
}
```

### C++（次）
```cpp
class Solution {
public:
    int gcdOfOddEvenSums(int n) {
        // 同 Java：sumOdd = n^2, sumEven = n*(n+1)
        // gcd(n^2, n*(n+1)) = n（相鄰整數互質）
        return n;
    }
};
```

## 5. 時間複雜度推導
沒有任何迴圈或遞迴 —— 整個函式只是回傳一個常數運算（一次賦值/回傳）。無論 `n` 多大（本題上限 `n ≤ 1000`，但即使 `n` 到 `10^9` 也一樣），執行的機器指令數都固定，因此時間複雜度為 `O(1)`。

（對照：若照天真解法真的去算 `sumOdd = n²`、`sumEven = n(n+1)`，再跑 Euclidean algorithm 求 GCD，兩數大小約 `O(n²)`，Euclidean algorithm 的迭代次數是 `O(log(min(a,b)))`，也就是 `O(log n)` —— 仍然非常快，但比起直接推導出 `O(1)` 的封閉解，多做了完全不必要的計算。）

## 6. 空間複雜度推導
沒有配置任何額外陣列、集合或遞迴呼叫堆疊，只用了函式參數本身，因此空間複雜度為 `O(1)`。

## 7. 模式歸納
屬於「**數論封閉式化簡（Math / Number Theory closed-form simplification）**」模式：拿到題目後不要急著寫迴圈，先用等差數列求和公式、GCD 的因式分解性質（`gcd(ka, kb) = k·gcd(a,b)`）、相鄰整數互質等基本數論工具，看能不能把答案推導成一個常數表達式。

**辨識特徵**：
- 題目描述「前 n 個某某數之和」→ 先想等差數列求和公式，而非累加迴圈。
- 要求兩個表達式的 GCD/LCM，且兩表達式明顯共享因子 → 嘗試提出公因子化簡。
- 資料範圍很小、標籤是 Math/Number Theory → 高機率存在 `O(1)` 封閉解。

**相關/變形題**：像「Sum of first n natural numbers」「GCD of two numbers derived from arithmetic sequences」等變形，都可以用同樣「先求封閉式、再用 GCD 因式分解性質化簡」的兩步驟套路。

## 8. 踩坑 / 易錯點
- **邊界 `n = 1`**：`sumOdd = 1`，`sumEven = 2`，`gcd(1, 2) = 1 = n`，公式仍成立，不需要特判。
- 若沒推導到底、只做到「`sumOdd = n²`, `sumEven = n(n+1)`」就直接呼叫語言內建的 `gcd()` 函式，答案雖然一樣正確（見下方社群解法對照），但這是「半吊子推導」——白白多做了乘法與輾轉相除法的計算，也錯過了這題真正想考的「相鄰整數互質」洞察。
- 容易誤用求和公式：奇數和公式是 `n²`（不是 `n(n+1)`，那是偶數和或自然數和的二倍），偶數和是 `n(n+1)`（不是 `2n²` 或 `n²+1`），這兩個公式很容易搞混，建議用 `n=4` 的範例（`sumOdd=16=4²`, `sumEven=20=4×5`）在心裡快速驗證一次再下筆。
- 本題資料型別上不會溢位（`n ≤ 1000` 時 `sumEven` 最大約 `1000×1001 ≈ 10^6`，`int` 綽綽有餘），但如果未來變形題把上限拉高到 `10^9` 等級，`sumOdd = n²` 會超過 `int` 範圍，需改用 `long`／`long long`——這也是為什麼直接推導出「答案就是 n」比起真的去計算兩個 sum 更穩健，不必擔心中間值溢位。

## 9. 社群解法對照

- **🏆 社群主流解**：五篇高票解法在核心結論上完全一致——`sumOdd = n²`、`sumEven = n(n+1)`，兩者的 GCD 恆等於 `n`，因此最簡潔寫法就是直接 `return n;`，社群共識與本解法相同。[查看原文](https://leetcode.com/problems/gcd-of-odd-and-even-sums/solutions/7115082/)
- **⚡ 另一種取向**：LeadingTheAbyss 的解法選擇「保守派」寫法——先算出 `sumOdd`、`sumEven` 兩個實際數值，再呼叫內建 `gcd()` 函式做真正的輾轉相除法，而非直接推導成 `n`；效能上仍是 `O(log n)` 級別、幾乎沒有差別，但這種寫法更貼近題目字面、對還沒把握「相鄰整數互質」證明的人來說更保險，也留下驗證原始邏輯的痕跡。[查看原文](https://leetcode.com/problems/gcd-of-odd-and-even-sums/solutions/7115094/)
- **💡 講得最好的一篇**：rosvert 的「Why return n works?」用最精簡的五步驟代數推導（求和公式 → 提出公因子 `n` → 指出 `n` 與 `n+1` 互質 → 結論恆為 `n`），邏輯清楚、沒有廢話，最適合拿來當這題的標準推導範本。[查看原文](https://leetcode.com/problems/gcd-of-odd-and-even-sums/solutions/8397686/)
