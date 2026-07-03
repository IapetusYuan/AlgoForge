---
id: 1
title: Two Sum
slug: two-sum
difficulty: Easy
tags: [Array, Hash Table]
url: https://leetcode.com/problems/two-sum/
patterns: [hash-map, space-time-tradeoff, complement-lookup]
time_complexity: O(n)
space_complexity: O(n)
date_solved: 2026-06-22
revisit: 2026-06-29
status: solved
---

# 1. Two Sum

> Easy · Array, Hash Table · [原題連結](https://leetcode.com/problems/two-sum/)

## 題目原文
Given an array of integers `nums` and an integer `target`, return *indices of the two numbers such that they add up to `target`*.

You may assume that each input would have ***exactly* one solution**, and you may not use the *same* element twice.

You can return the answer in any order.

 

Example 1:**

```
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

Example 2:**

```
Input: nums = [3,2,4], target = 6
Output: [1,2]
```

Example 3:**

```
Input: nums = [3,3], target = 6
Output: [0,1]
```

 

**Constraints:**

	- `2 <= nums.length <= 10^4`

	- `-10^9 <= nums[i] <= 10^9`

	- `-10^9 <= target <= 10^9`

	- **Only one valid answer exists.**

 

**Follow-up: **Can you come up with an algorithm that is less than `O(n^2)` time complexity?

---
## 1. 題目摘要

給整數陣列 `nums` 和目標 `target`，找出**兩個數相加等於 target** 的那組**索引**回傳。保證恰有一組解、同一元素不可用兩次。限制：`n ≤ 1e4`，值可為負（`-1e9 ~ 1e9`）。

## 2. 怎麼切入這題（思維框架）

**第一個天真念頭**：兩兩配對都試一遍 —— 雙層迴圈枚舉所有 `(i, j)`，檢查 `nums[i] + nums[j] == target`。這能 work，但是 `O(n²)`。題目的 Follow-up 直接點名「能不能比 `O(n²)` 更快？」，等於明示要優化。

**怎麼把 O(n²) 砍掉？** 觀察內層迴圈在做什麼：固定 `nums[i]`，它在**找有沒有另一個數等於 `target - nums[i]`**。這是一個「查找」動作。

**關鍵反射**：凡是「我手上有個值 x，想知道之前有沒有出現過某個特定值」→ 把看過的東西丟進 **HashMap**，查找從 `O(n)` 變 `O(1)`。

於是切入點 = **邊掃邊存**：對每個 `nums[i]`，先算它的「互補數」`need = target - nums[i]`，去 map 裡查有沒有；有就回傳配對索引，沒有就把 `nums[i] → i` 存進 map 繼續。一趟掃完。

**為什麼存「值→索引」而不是「索引→值」？** 因為我們查的時候手上有的是「想要的值」（互補數），要用值反查索引，所以 key 必須是值。

## 3. 核心觀念

- **雜湊表查找（hash map lookup）**：把「線性搜尋」換成「O(1) 雜湊查找」，這是把 `O(n²)` 降到 `O(n)` 最常見的手法。
- **以空間換時間（space-time tradeoff）**：多用一個 `O(n)` 的 map，換來時間從 `O(n²)` → `O(n)`。
- **互補數 / 一趟掃描（one-pass）**：不需要先建好整張表再找；邊建邊查就夠，因為配對的另一半一定在「更早出現」或「更晚出現」其中一邊，掃過去必定相遇。

## 4. 解法

### Java（主）
```java
class Solution {
    public int[] twoSum(int[] nums, int target) {
        // key = 出現過的數值, value = 它的索引
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int need = target - nums[i];      // 我還缺這個互補數
            if (seen.containsKey(need)) {     // 之前出現過 → 配成一對
                return new int[]{seen.get(need), i};
            }
            seen.put(nums[i], i);             // 沒配到，記下自己供之後查
        }
        return new int[]{};                   // 題目保證有解，理論上不會到這
    }
}
```

### C++（次）
```cpp
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> seen;          // 值 -> 索引
        for (int i = 0; i < (int)nums.size(); ++i) {
            int need = target - nums[i];
            auto it = seen.find(need);
            if (it != seen.end()) return {it->second, i};
            seen[nums[i]] = i;
        }
        return {};
    }
};
```

## 5. 時間複雜度推導

- 只有一個 for 迴圈，跑 `n` 次。
- 迴圈內：`containsKey` / `find` 與 `put` 都是雜湊表操作，平均 `O(1)`。
- 加總：`n × O(1) = ` **`O(n)`**。
- 對照天真解雙層迴圈 = `n + (n-1) + … = O(n²)`，HashMap 把內層那次線性查找壓成常數。
- （極端情況雜湊全衝突會退化成 `O(n)` 單次查找 → 最壞 `O(n²)`，但平均與實務是 `O(n)`。）

## 6. 空間複雜度推導

- 額外用一個 `seen` map，最壞情況把幾乎所有元素都存進去（找到答案前）→ 最多 `n` 個 entry → **`O(n)`**。
- 這就是「空間換時間」付出的空間代價。

## 7. 模式歸納

- **模式**：`HashMap 互補查找 / one-pass`。
- **辨識特徵**：題目要你「找兩個（或一組）元素滿足某個加總/差值/配對關係」→ 想「固定一個，另一個能不能 O(1) 查到」→ HashMap。
- **相關/變形題**：
  - [[167-two-sum-ii-input-array-is-sorted]]（已排序 → 改用**雙指標** `O(1)` 空間，是另一條路：排序好就不必雜湊）
  - [[15-3sum]]（三數和 = 固定一個 + 對剩下做 Two Sum）
  - [[1-two-sum]] 的進階：若要回傳「值」而非索引且陣列可排序，雙指標更省空間。
  - 心法延伸：「之前有沒有出現過某值」這個查找模式，也用在 [[560-subarray-sum-equals-k]]（前綴和 + HashMap）。

## 8. 踩坑 / 易錯點

- **不能用同一元素兩次**：所以要「先查再存」。如果寫成先把全部存進 map 再查，遇到 `target = 2*nums[i]` 會把自己當成互補數配到自己。一趟「先查後存」天然避開。
- **重複值**：例如 `[3,3], target=6`。先查（map 空，沒中）→ 存 `3→0`；第二個 3 查到 `3`，回傳 `[0,1]`，正確。若用「值→索引」且後存覆蓋前者也沒關係，因為配對當下就回傳了。
- **負數 / 大數**：值域 `±1e9`，兩數相加可能到 `2e9` **超過 int 上限**（int 約 2.1e9，剛好邊緣）。本解法算的是 `target - nums[i]`，落在 `±2e9`，Java 的 `target - nums[i]` 仍是 int 運算可能溢位 → 嚴謹起見可用 `long need = (long)target - nums[i];`。實務上 LeetCode 此題測資不會踩到，但面試講出這點是加分。
- **回傳順序**：題目說任意順序，`{seen.get(need), i}` 天然是「先出現的在前」。

---

> **這題教會你的一招**：要找「滿足某關係的一對元素」時，把「內層線性搜尋」換成「HashMap O(1) 查找」，用 O(n) 空間把時間從 O(n²) 砍到 O(n) —— 這是刷題最高頻的一招，務必形成反射。
